# vulrem — Vulnerability Remediaton
Version 0.1
by Mikhail Kondrashin

[![License](https://img.shields.io/badge/License-Apache%202-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This solution integrate two Trend Micro Security Solutions:
[CloudOne Container Security](https://www.trendmicro.com/en_my/business/products/hybrid-cloud/cloud-one-container-image-security.html)
(AKA [Deep Security Smart Check](https://deep-security.github.io/smartcheck-docs/admin_docs/admin.html))
and [CloudOne Workload Security](https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one-workload-security.html)
(AKA [Trend Micro Deep Security](https://help.deepsecurity.trendmicro.com/))

VulRem automatically turns on Trend Micro Deep Security IPS filters (called virtual patches)
for each vulnerability found by Deep Security Smart Check.  

VulRem can be handy in case Smart Check detects a vulnerable component,
but developers can not update it as it will break their code. In this case
virtual patching feature of Deep Security can help and mitigate 
the threat for some time provided availability 
of appropriate IPS filter.

It is designed to run as CronJob on the same Kubernetes cluster
as Deep Security Smart Check, though it can run as script
or in container (see Post Scriptum).

**Note:** VulRem does not initiate registry scans,
but uses last scan result.

### Configure Trend Micro Deep Security

#### Create custom policy
Open Deep Security Web console, and go to **Policies** and create new policy
or pick existing policy that will be configured
by VulRem. This policy should be the root policy for
all servers running containers. 

#### Get policy ID
To determine this policy ID, right click on it and pick "**Detailes...**" menu item. 
Check URL of popup browser window. It should look like
```html
https://<your DSM address>:4119/PolicyEditor.screen?securityProfileID=X
```
This "X" is required policy ID.

#### Generate API key
Go to **Administration** > **User Management** > **Roles**
and press "**New...**" button.
* Name new Role "VulRem Access", though name 
can be arbitrary
* Uncheck "Allow Access to Deep Security Manager User Interface"
* Check "Allow Access o web services API"
* On **Policy Rights** tab check **Allow Users to: Edit**
* Check **Selected Policies** option
* Pick policy created or chosen on previous step
* Press **OK** button

**Note**: One can skip creating custom role and use **Full Access** for API key,
though it is less secure.  

Go to **Administration** > **User Management** > **API Keys**
and press "**New...**" button.
* Name new API key "VulRem", though name can be arbitrary
* Choose **Role** created above
* Click **Next...**
* Save API key

### Configure Deep Security Smart Check

Login to Smart Check as **administrator** and go to **Users**. Click **+ CREATE** button.
Create new user with **Auditor** role.

**Note**: regular administrator account can be used,
though this is less secure.

### Configure vulrem CronJob

Edit vulrem_secrets.yaml file (keep quotes around values):
 ```yaml
apiVersion: v1
kind: Secret
metadata:
  name: "vulremsecrets"
type: Opaque
stringData:
    SMARTCHECK_USERNAME: "Name of Smart Check user with auditor role"
    SMARTCHECK_PASSWORD: "Password of this user"
    DEEPSECURITY_API_KEY: "Deep Security API key"
```

Provide appropriate values for the following variables:
* SMARTCHECK_USERNAME
* SMARTCHECK_PASSWORD
* DEEPSECURITY_API_KEY

Edit vulrem_cronjob.yaml file:
```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: "vulrem-cron"
spec:
  schedule: "0 1 * * *" # Run once a day at 1 a.m.
  jobTemplate:
    spec:
      template:
        spec:
          replicas: 1
          restartPolicy: OnFailure
          containers:
            - name: "vulrem"
              image: "mpkondrashin/vulrem"
              imagePullPolicy: Always
          env:
            - name: DEEPSECURITY_POLICY_ID
              value: "Policy ID"
            - name: DEEPSECURITY_URL
              value: "https://DSM address:4119/api"
            - name: SMARTCHECK_SKIP_TLS_VERIFY
              value: "True"
            - name: DEEPSECURITY_SKIP_TLS_VERIFY
              value: "True"
            - name: SMARTCHECK_USERNAME
              valueFrom:
                secretKeyRef:
                  name: vulremsecrets
                  key: SMARTCHECK_USERNAME
            - name: SMARTCHECK_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: vulremsecrets
                  key: SMARTCHECK_PASSWORD
            - name: DEEPSECURITY_API_KEY
              valueFrom:
                secretKeyRef:
                  name: vulremsecrets
                  key: DEEPSECURITY_API_KEY
```

Provide appropriate values for the following variables:
* schedule
* DEEPSECURITY_POLICY_ID
* DEEPSECURITY_URL
* SMARTCHECK_SKIP_TLS_VERIFY 
* DEEPSECURITY_SKIP_TLS_VERIFY
* SMARTCHECK_USERNAME

Run following command on Kubernetes:
```shell
$ kubectl apply -f vulrem_secrets.yaml 
$ kubectl apply -f vulrem_cronjob.yaml 
```

This is it!

### Test VulRem

To test vulrem run following command:
```shell
$ kubectl create job --from=cronjob/vulrem-cron vulrem-test
```

To check vulrem logs use following command:
```shell
$ kubectl logs jobs/vulrem-test
```

### VulRem in action

After successful completion of policy configuration,
VulRem makes two changes to chosen policy:
* Appropriate Intrusion Prevention module filters are turned on
* Description is populated with list of CVEs that present in one
of container images, but can not be covered by any of 
  Deep Security IPS rules
  
## P.S. Running VulRem not in K8s
Preparation steps for Deep Security and Smart Check are the same.
### Running as separate script

Python 3.x is required.

Install required modules:
```shell
$ pip install requests docker-image-py
$ pip install https://automation.deepsecurity.trendmicro.com/sdk/20_0/v1/dsm-py-sdk.zip
```

Edit **run_main.sh** to define appropriate environment variables
and run it.

### Running in container

Pull container from Docker Hub using following command:
```shell
$ docker pull mpkondrashin/vulrem
```
or install required modules (see above) and build your container
from source:
```shell
$ docker build --tag vulrem .
```
Create env.list file:
```shell
SMARTCHECK_URL=https://<DSSC Address>:<DSSC Port>
SMARTCHECK_SKIP_TLS_VERIFY=True
SMARTCHECK_USERNAME=<username>
SMARTCHECK_PASSWORD=<password
DEEPSECURITY_URL=https://<DSM address>:4119/api
DEEPSECURITY_SKIP_TLS_VERIFY=True
DEEPSECURITY_API_KEY=<API key>
DEEPSECURITY_POLICY_ID=<Policy ID>
```
Run container using following command:
```
$ docker run --env-file env.list mpkondrashin/vulrem
```
or 
```
$ docker run --env-file env.list vulrem
```
if your have built container from the source.

