# BigChainDBDriver
A driver for transactions with multiple users and Crypto-Conditions.

The goal of this driver is to implement the following, with multiple users:
1. Create and Transfer
2. Threshold Conditions
3. Hash Conditions 

The current format allows for transactions to multiple users. For example, if one wants to transfer a transaction to N users, one can input their public keys in the transfer transaction, rather than calling the API N times.

**Note that currently, all API's work and have been tested, except for the thresholdTransfer endpoint. It is currently being worked on. Hash Conditions are to come very soon.** To implement threshold conditions for a transaction, one must use the tresholdTransfer endpoint after using the generateThresholdConditions endpoint.

**Please see the Driver.py file for API input comments and examples. An easy guide with examples will be put in this read-me in the next couple of days. In particular, for JSON objects, one needs to use double quotes rather than single quotes. Numeric values should be inputted as strings rather than integers. When it is appropriate for multiple users, separate public keys and private keys with the delimiter "_"**


After downloading the file, place it in a directory. For example, you may run,


	mkdir BigchainDriver


To run the driver, issue the following command in your directory:


	python Driver.py


The api is exposed at your local host at port 5000. To access it from a different server, simply type the ip. That is, 

	http://<ip>:5000/


Thanks to bigchain community for making bigchain such an easy and straightforward tool! Please feel to contact with any comments/concerns or added requested functionality!

