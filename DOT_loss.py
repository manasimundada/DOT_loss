from flask import Flask, render_template, request
from substrateinterface import SubstrateInterface, Keypair

app = Flask(__name__)

# Set up Substrate interface
substrate_connection = SubstrateInterface(
    url="ws://127.0.0.1:9944",
    ss58_format=0,
    type_registry_preset='polkadot'
)
alice_keypair = Keypair.create_from_uri('//Alice')

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""
    if request.method == 'POST':
        target_address = request.form.get('target_address')
        transfer_amount = request.form.get('transfer_amount')
        
        if target_address and transfer_amount:
            try:
                transfer_value = int(transfer_amount)
                message = calculate_dot_loss(target_address, transfer_value)
            except ValueError:
                message = "Invalid input: Amount must be a number"
        else:
            message = "Please fill in both the target address and the amount."
    
    return render_template('index.html', message=message)

def calculate_dot_loss(target, value):
    # Convert amount to the smallest unit (Planck)
    micro_units = value * 10**15  
    
    # Compose the call to transfer balance
    transaction_call = substrate_connection.compose_call(
        call_module='Balances',
        call_function='transfer',
        call_params={
            'dest': target,
            'value': micro_units
        }
    )
    
    # Get the payment info
    fee_info = substrate_connection.get_payment_info(call=transaction_call, keypair=alice_keypair)
    
    # Calculate the DOT loss
    dot_loss = value + (fee_info['partialFee'] / 10**15)
    
    return f"Target Address: {target}, Transfer Amount: {value}\nEstimated DOT Loss: {dot_loss}"

if __name__ == '__main__':
    app.run(debug=True)
