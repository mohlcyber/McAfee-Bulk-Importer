# McAfee-Bulk-Importer

This is a small project to provide the ability to import multiple hashes into the McAfee TIE database as well as allowing to actively run McAfee Active Response lookups. I will add the MVISION EDR hash lookup in the future.

## Preperation

1. Python 3.x, Flask and OpenDXL libraries:  ```pip install flask dxlclient dxltieclient```

2. Access to a McAfee ePolicy Orchestrator (Username / Password). Enter the ip and credentials in line 23 - 26. getpass and args will be added in the future.

3. OpenDXL Certificate Files Creation ([Link](https://github.com/opendxl/opendxl-client-python/blob/master/docs/sdk/basiccliprovisioning.rst)).

4. Make sure to authorize the new created certificates in ePO to set McAfee TIE Enterprise Reputations as well as External Reputations ([Link](https://opendxl.github.io/opendxl-tie-client-python/pydoc/basicsetreputationexample.html)).

5. Make sure that the FULL PATH to the config file is entered in line 21 (process.py).

## Execution

Run the script ```python3.7 process.py``` and access the webpage via ```http://127.0.0.1:5000```.

![Screenshot 2020-08-04 at 14 58 16](https://user-images.githubusercontent.com/25227268/89296679-f42dc200-d662-11ea-9695-14c98ff7dcef.png)

Now upload a csv file that includes one of the following headers: 'md5', 'sha1', 'sha256', 'hostname'.
The app will automatically look for values in these columns. 

Select TIE Reputation or EDR lookup and click submit.

![Screenshot 2020-08-04 at 14 59 00](https://user-images.githubusercontent.com/25227268/89296737-0d367300-d663-11ea-994e-4dd52f14d7d3.png)

The app contains a quarantine option. Systems that responded to the EDR/MAR query can be selected and quarantined.
Systems that are already quarantined can be un-quarantined. Please be careful in quarantining systems via the app because of the direct impact to the selected system.

![Screenshot 2020-08-04 at 15 00 30](https://user-images.githubusercontent.com/25227268/89296861-453db600-d663-11ea-9a38-5181d66dd578.png)

Please provide any feedback via comments or issues in Github.
