import asyncio, sys, click, os, yaml
from monstr.encrypt import Keys
from monstr.client.client import Client, ClientPool
from monstr.event.event import Event
from safebox.wallet import Wallet
from safebox.models import nostrProfile, SafeboxItem
from datetime import datetime
from safebox.wallet import Wallet
from safebox.lightning import lightning_address_pay

relays  = ["wss://nostr-pub.wellorder.net", "wss://relay.damus.io"]
mints   = ["https://8333.space:8333"]
wallet  = "default" 

home_directory = os.path.expanduser('~')
cli_directory = '.safebox'
config_file = 'config.yml'
config_directory = os.path.join(home_directory, cli_directory)
file_path = os.path.join(home_directory, cli_directory, config_file)

os.makedirs(config_directory, exist_ok=True)

if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        config_obj = yaml.safe_load(file)
else:
    config_obj = {'nsec': 'notset', 'relays': relays, "mints": mints, "wallet": wallet}
    with open(file_path, 'w') as file:        
        yaml.dump(config_obj, file)

RELAYS  = config_obj['relays']
NSEC    = config_obj['nsec']
MINTS   = config_obj['mints']
WALLET  = config_obj['wallet']

def write_config():
     with open(file_path, 'w') as file:        
        yaml.dump(config_obj, file)



@click.group()
def cli():
    pass

@click.command()
@click.pass_context
def info(ctx):
    click.echo("This is safebox")
    click.echo(ctx.obj)

@click.command(help="create a new safebox")
def create():
    click.echo("Creating a new safebox")
    wallet_obj = Wallet(NSEC, RELAYS, MINTS)
    config_obj['nsec'] = wallet_obj.create_profile()
    click.echo(f"nsec: {config_obj['nsec']}")
    write_config()
    click.echo(wallet_obj.get_post())
    


@click.command(help="set local config options")
@click.option('--nsec', '-n', default=None, help='set nsec')
@click.option('--relays', '-r', default=None, help='set relays')
@click.option('--mints', '-m', default=None, help='set mints')
@click.option('--wallet', '-w', default=None, help='set wallet')
def set(nsec, relays, mints, wallet):
    if nsec == None and relays == None and mints == None and wallet==None:
        click.echo(yaml.dump(config_obj, default_flow_style=False))
        return
   

    if nsec != None:
        config_obj['nsec']=nsec
    if relays != None:
        print("relays:", relays)
        relay_array = str(relays).replace(" ","").split(',')
        relay_array_wss = []
        for each in relay_array:
            relay_array_wss.append(each if "wss://" in each else "wss://"+each)
        print(relay_array_wss)
        config_obj['relays']=relay_array_wss
    else:
       config_obj['relays']=RELAYS 

    if mints != None:
        
        mint_array = str(mints).replace(" ","").split(',') 
        mint_array_https = []
        for each in mint_array:
            mint_array_https.append(each if "https://" in each else "https://"+each)

        config_obj['mints']=mint_array_https
        print("setting mints" , mint_array_https)
       
    else:
       config_obj['mints']=MINTS 

    if wallet != None:
        config_obj['wallet'] = wallet
    else:
        config_obj['wallet'] = WALLET

    # print(config_obj)
    click.echo(yaml.dump(config_obj,default_flow_style=False))
    with open(file_path, 'w') as file:        
        yaml.dump(config_obj, file)


@click.command()
# @click.option('--nsec', '-n', help='nsec for wallet')
def profile():
    wallet = Wallet(NSEC, RELAYS, MINTS)
    nostr_profile = wallet.get_profile()
    click.echo(f"npub: {str(wallet.pubkey_bech32)}")
    click.echo(f"nsec: {str(wallet.k.private_key_bech32())}")
    click.echo("-"*80)
    for key, value in nostr_profile.items():
        
        click.echo(f"{str(key).ljust(15)}: {value}")
    click.echo("-"*80)
    click.echo(wallet.get_post())
    click.echo("-"*80)
    # click.echo(wallet.get_proofs())

@click.command(help='help for getwalletinfo')
@click.option('--wallet', '-w', default = None, help='wallet name')
def getwalletinfo(wallet):
    if wallet != None:
        print(wallet)
    else:
        print(WALLET)
        wallet = WALLET
    
    wallet_obj = Wallet(NSEC, RELAYS)

    try:
        wallet_info = wallet_obj.get_wallet_info(d_tag=wallet)

    except:
        wallet_info = "No wallet found!"
    
    click.echo(wallet_info)

@click.command(help='help for setwalletinfo')
@click.option('--wallet', '-w', default = None, help='wallet name')
@click.option('--mints', '-m', help='list of mints')
@click.option('--jsons', '-j', help='json string')
def setwalletinfo(wallet, mints, jsons):
    wallet_obj = Wallet(NSEC, RELAYS)
    # click.echo(wallet.get_wallet_info())
    click.echo(wallet)
    if mints != None:
        mint_array = str(mints).replace(" ","").split(',')
        # click.echo(mints if "https://" in mint else "https://"+mint)
        click.echo(mint_array)
    else:
        mint_array = config_obj['mints']
    
    wallet_info_now = f"test time {datetime.now()}"
    if jsons != None:
        wallet_info = jsons
    else:
        wallet_info = "{'test':'test'}"

    if wallet != None:
        wallet_name = wallet
    else:
        wallet_name = config_obj['wallet']
        print("wallet_name", wallet)
    
    relay_array = config_obj['relays']
    wallet_obj.set_wallet_info(wallet_name, mint_array,relays=relay_array, wallet_info=wallet_info)

@click.command(help='Do a post')
@click.option('--message','-m', default='hello world')
def post(message):
    click.echo(message)
    wallet_obj = Wallet(NSEC, RELAYS, MINTS)
    wallet_obj.send_post(message)

@click.command(help='help for setindexinfo')
@click.option('--jsons', '-j', default = '{}', help='json string')
def setindexinfo(jsons):
    click.echo("setindex info")
    wallet_obj = Wallet(NSEC, RELAYS)
    wallet_obj.set_index_info(jsons)

@click.command(help='help for getindexinfo')
def index():
    click.echo("getindex info")
    wallet_obj = Wallet(NSEC, RELAYS)
    index_out = wallet_obj.get_index_info()
    if index_out:
        click.echo(index_out)
    else:
        click.echo("No index!")

@click.command(help='help for getindexinfo')
def additem():
    click.echo("add safebox item")
    safe_box_item = SafeboxItem(name="test",type="note",description="test")
    print(safe_box_item.gethash())
    wallet_obj = Wallet(NSEC, RELAYS)
    index_out = wallet_obj.add_item(safe_box_item)
    click.echo(index_out)

@click.command(help="Deposit funds into wallet")
@click.argument('amount')
def deposit(amount: int):
    click.echo(f"amount: {amount}")
    wallet_obj = Wallet(NSEC, RELAYS,MINTS)
    msg_out = wallet_obj.deposit(amount)
    click.echo(msg_out)
    

@click.command(help="Payout funds to lightning address")
@click.option('--lnaddress','-l', default='trbouma@walletofsatoshi.com')

def payout(lnaddress: str):
    click.echo(f"Pay out to: {lnaddress}")
    wallet_obj = Wallet(NSEC, RELAYS,MINTS)
    wallet_obj.payout(lnaddress)
    
    
    #click.echo(msg_out)

@click.command(help="List proofs")
def proofs():
    
    wallet_obj = Wallet(NSEC, RELAYS, MINTS)
    # msg_out = wallet_obj.get_proofs()
    # wallet_obj.delete_proofs()
    # click.echo(msg_out)
    click.echo(f"{wallet_obj.balance} sats in {len(wallet_obj.proofs)} proofs in {wallet_obj.events} events")
    click.echo(f"{wallet_obj.powers_of_2_sum(wallet_obj.balance)}")

@click.command(help="Swap proofs")
def swap():
    
    wallet_obj = Wallet(NSEC, RELAYS, MINTS)
    # msg_out = wallet_obj.get_proofs()
    # wallet_obj.delete_proofs()
    # click.echo(msg_out)
    click.echo(wallet_obj.swap())

cli.add_command(info)
cli.add_command(create)
cli.add_command(profile)
cli.add_command(post)

cli.add_command(set)
cli.add_command(payout)
cli.add_command(getwalletinfo)
cli.add_command(setwalletinfo)
cli.add_command(setindexinfo)
cli.add_command(index)
cli.add_command(additem)
cli.add_command(deposit)
cli.add_command(proofs)
cli.add_command(swap)


if __name__ == "__main__":
   cli()