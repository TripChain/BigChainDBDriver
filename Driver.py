#Flask is the library that allows one to make a RESTful service in Python
import flask
import copy
import json

#These libraries let one get API requests and make data in JSON format
from flask import Flask
from flask import jsonify
from flask import request

#libraries for bigchain functionality
from bigchaindb import Bigchain
from bigchaindb import crypto
from bigchaindb import util
import cryptoconditions as cc


app = Flask(__name__)


#generate a public and private key (internal user)
priv,pub = crypto.generate_key_pair()

#instantiate your chain
b = Bigchain()


#GET: public and private key of a new user to be generated
#User Input: None
@app.route('/getKeys', methods=['GET'])
def get_keys():
        priv1,pub1 = crypto.generate_key_pair()
        return jsonify({'public key': pub1, 'private key': priv1})


#POST: a transfer transaction
#User Input: A json object, an example is shown below:
# {"conID": "0", 
#  "pubFrom" : "this is a public key of the sender",
#  "pubTo: "this is a public key of the recipient", 
#  "privFrom" : "this is the private key of the sender",
#  "txID: "this is the transaction id for the transfer"}
@app.route('/transaction', methods = ['POST'])
def transaction():
        input = request.get_json(force=True)
        pubTo = str(input['PubTo'])
        pubFrom =str(input['PubFrom'])
        privFrom = str(input['PrivFrom'])
        txID = str(input['txID'])
        conID = int(input['conID'])
        txANDcon = {"cid":conID, "txid": txID}
        
        tx_transfer = b.create_transaction(pubFrom, pubTo,
                                       txANDcon, 'TRANSFER')
        tx_transfer_signed = b.sign_transaction(tx_transfer,
                                                privFrom)
        b.write_transaction(tx_transfer_signed)
        return flask.jsonify(**tx_transfer_signed)



#POST: Add a transaction (default internal user)
#User Input: A digital asset payload, example shown below
# {"msg": "hi"}
@app.route('/addData/default', methods=['POST'])
def add_data():
        digital_asset_payload = request.get_json(force=True)
        tx = b.create_transaction(b.me, pub, None, 'CREATE',
                                   payload = digital_asset_payload)
        tx_signed = b.sign_transaction(tx, b.me_private)
        b.write_transaction(tx_signed)
        return flask.jsonify(**tx_signed)


#POST: Add a transaction
#User Input: A digital asset payload, public key
#The digital asset payload is the post request data in json format;
#The public key should be put into the URL
@app.route('/addData/<pub1>', methods=['POST'])
def add_data_2(pub1):

        digital_asset_payload = request.get_json(force=True)
        tx = b.create_transaction(b.me, pub1.split("_"), None, 'CREATE',
                                  payload = digital_asset_payload)
        tx_signed = b.sign_transaction(tx, b.me_private)
        b.write_transaction(tx_signed)
        return flask.jsonify(**tx_signed)



#POST: Implement a Threshold Condition Transaction
#Input is a Json object. An example is shown below.
#{
# "pubNew": "these are public keys of the receivers in the transaction"
# "txID": "this is the threshold transaction id"
# "cid": "this is the threshold condition id"
# "pubKeys": "these are the public keys of EVERYONE in the threshold agreement"
# "privKeys": "SAME ORDER. these are the private keys of the threshold agreement.Ofcourse, it must be at least the threshold number."
# "N": "this is the threshold number of the transaction"
#}

@app.route('/thresholdTransaction', methods = ['POST'])
def threshold_it_2():
        #get data
        data = request.get_json(force=True)
        pubNew = data['pubNew']
        txID = data['txID']
        cid = int(data['cid'])
        pubKeys = data['pubKeys']
        privKeys = data['privKeys']
        N = int(data['N'])

        #format data
        pubNew = pubNew.split("_")
        pubKeys = pubKeys.split("_")
        privKeys = privKeys.split("_")
        txn  = {"cid": cid, "txid": txID}

        #this is the subfulfillment list. we use pubKeys initially as it has the same size.
        subfulfillments = pubKeys

      
        threshold_tx_transfer = b.create_transaction(pubKeys, pubNew, txn, 'TRANSFER')

        privKeys = privKeys.split("_")
        txn  = {"cid": cid, "txid": txID}

        #this is the subfulfillment list. we use pubKeys initially as it has the same size.
        subfulfillments = pubKeys

        threshold_tx_transfer = b.create_transaction(pubKeys, pubNew, txn, 'TRANSFER')

        threshold_tx = b.get_transaction(txID)
        threshold_fulfillment = cc.Fulfillment.from_json(threshold_tx['transaction']['conditions'][0]['condition']['details'])

        for i in range(len(pubKeys)):
                subfulfillments[i] = threshold_fulfillment.get_subcondition_from_vk(pubKeys[i])[0]

        threshold_tx_fulfillment_message = util.get_fulfillment_message(threshold_tx_transfer,
                                                                threshold_tx_transfer['transaction']['fulfillments'][0],
                                                                serialized=True)

        threshold_fulfillment.subconditions = []

        for i in range(N):
                subfulfillments[i].sign(threshold_tx_fulfillment_message, crypto.SigningKey(privKeys[i]))
                threshold_fulfillment.add_subfulfillment(subfulfillments[i])


        # Add remaining (unfulfilled) fulfillment as a condition
        for i in range(len(pubKeys)-N):
                threshold_fulfillment.add_subcondition(subfulfillments[i+N].condition)

        threshold_tx_transfer['transaction']['fulfillments'][0]['fulfillment'] = threshold_fulfillment.serialize_uri()


        b.write_transaction(threshold_tx_transfer)


        return flask.jsonify(**threshold_tx_transfer)
        
        
# #POST:
#This does the following. It adds threshold conditions in a transaction to new users.
#And your threshold condition is made. Then (and only then) can you use thresholdTransaction Request.
#
#Input is a json object. Example shown below
#{
# "txID": "this is the transaction id to be transferred to new users"
# "cid": "this is the condition id of the transaction"
# "pubKeys": "these are public keys of owners ex. pub1_pub2_pub3"
# "privKeys": "these are private keys of owners ex. priv1_priv2_priv3"
# "newPubKeys" : "these are public keys of the new owners"
# "N" : "this is the threshold number"
#}
@app.route('/generateThresholdConditions', methods=['POST'])
def threshold_it():

        #gets input data
        data = request.get_json(force=True)
        txID = data['txID']
        cid = int(data['cid'])
        pubKeys = data['pubKeys']
        privKeys = data['privKeys']
        newPubKeys = data['newPubKeys']
        N = int(data['N'])

        #formats input data
        pubKeys = pubKeys.split("_")
        privKeys = privKeys.split("_")
        newPubKeys = newPubKeys.split("_")

        #format retrieved_id
        txn  = {"cid": cid, "txid": txID}
        threshold_tx = b.create_transaction(pubKeys, newPubKeys,
                                            txn, 'TRANSFER')
 
        threshold_condition = cc.ThresholdSha256Fulfillment(threshold=(N))
        for i in range(len (newPubKeys)):
                threshold_condition.add_subfulfillment(
                cc.Ed25519Fulfillment(public_key=newPubKeys[i]))

        threshold_tx['transaction']['conditions'][0]['condition'] = {
        'details': json.loads(threshold_condition.serialize_json()),
        'uri': threshold_condition.condition.serialize_uri()}

        threshold_tx['id'] = util.get_hash_data(threshold_tx)

        threshold_tx_signed = b.sign_transaction(threshold_tx, privKeys)

        b.write_transaction(threshold_tx_signed)

        return flask.jsonify(**threshold_tx_signed)



#GET: Get Transaction
#User Input: Transaction ID into the URL
@app.route('/getTransaction/<tx_ID>', methods=['GET'])
def get_transaction(tx_ID):
        tx_retrieved = b.get_transaction(tx_ID)
        return flask.jsonify(tx_retrieved)



#run app
if __name__ == '__main__':
        app.run (
                host = "0.0.0.0",
                debug = True)
