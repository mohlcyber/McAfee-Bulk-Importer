# McAfee-Bulk-Importer

This is a small project to provide the ability to import multiple hashes into the McAfee TIE database as well as allowing to actively run McAfee Active Response lookups. I will add the MVISION EDR hash lookup in the future.

## Preperation

1. Python 3.x, Flask and OpenDXL libraries:  ```pip install flask dxlclient dxltieclient```

2. Access to a McAfee ePolicy Orchestrator (Username / Password)

3. OpenDXL Certificate Files Creation ([Link](https://github.com/opendxl/opendxl-client-python/blob/master/docs/sdk/basiccliprovisioning.rst)).

4. Make sure to authorize the new created certificates in ePO to set McAfee TIE Enterprise Reputations as well as External Reputations (Link).

5. Make sure that the FULL PATH to the config file is entered in line 21 (process.py).