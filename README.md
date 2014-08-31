Aqueduct
========

Asynchronous restful messages http bus

Overview
--------
If there are a lot of related web services it may be necessary to synchronize the data therebetween.
Most often, this problem is solved by developing individual api in each case. By increasing the
complexity of system, the logic of interaction of web services becomes a complex and implicit.

The second problem arises in situation described above: availability of services at the time
of sending a message: if pending service for any reason could not get the data - message may be lost
or problem of storage of unsent messages rests with the sender

The idea of ​​rest bus is a common messaging server to which all services sends information about
the changed data. Anybody who need to receive the data, subscribes to the appropriate channels.
In case of unavailability of recipient, message server can deliver unsent messages when
the recipient becomes  available.

A more detailed description and documentation will be available soon


Features
--------
* Configuring сhannels and recipients
* Receive messages over http protocol
* Delivery of messages with channelization
* Storage of undelivered messages
* Sending undelivered messages periodically as a task
* Support authorization api-key for application and in the recipient-services

Planned
--------------------
Ordering by priority:

* Reddis support
* Configuration by http
* Configuration in web interface
* Memcached support

