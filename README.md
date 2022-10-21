# Netapp-ONTAP-python-RESTApi

REST API offers a vastly simplified and workflow-driven user experience, allowing you to perform multiple operations on the storage objects with a single API. REST is the industry standard for API development and the ONTAP REST API provides a great opportunity to automate your storage deployments.

This repository contains sample scripts illustrating how to use the ONTAP REST API. You can access the API through the use of `requests` library. 

To install the requirements needed to run the simple script. Double click the `req.sh` file.

### Requirements
- Python 3.6 or higher
- requests 2.21.0 or later
- ONTAP 9 (NetApp storage system) or higher (untested on earlier versions)
- Install docopt
- Install prettytable


## Accessing the ONTAP REST API

The repository folder **examples/** contains sample scripts to directly access the ONTAP REST API using the `requests` library. You need to run each of the scripts with the appropriate parameters. Use the help provided with each script to get started. For example:

```
 python3 create_vol.py -s <STORAGE> -vm <SVM> -VN <VOLUME> <SIZE>
```