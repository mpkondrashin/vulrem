# vulrem — Vulnerability Remediator

[![License](https://img.shields.io/badge/License-Apache%202-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This solution integrate two Trend Micro Security Solutions:
[CloudOne Container Security](https://www.trendmicro.com/en_my/business/products/hybrid-cloud/cloud-one-container-image-security.html)
(AKA [Deep Security Smart Check](https://deep-security.github.io/smartcheck-docs/admin_docs/admin.html))
and [CloudOne Workload Security](https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one-workload-security.html)
(AKA [Trend Micro Deep Security](https://help.deepsecurity.trendmicro.com/))

VulRem automatically turns on Trend Micro Deep Security IPS filters (called virtual patches)
for each vulnerability found by Deep Security Smart Check.  

It is designed to run as CronJob on same Kubernetes cluster
as Deep Security Smart Check, though it can run as script
or in container (see Post Scriptum).

### Configure Trend Micro Deep Security

#### Create custom policy
Open Deep Security Web console and create new policy
or pick existing policy that will be configured
by vulrem. This policy should be the root policy for
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
* On "Policy Rights" tab check **Allow Users to: Edit**
* Check **Selected Policies**
* Pick policy created or chosen on previous step

**Note**: One can skip creating custom role and use **Full Access** for API key,
though it is less secure.  

Go to **Administration** > **User Management** > **API Keys**
and press "**New...**" button.
* Name new API key as VulRem, though name can be arbitrary
* Choose **Role** created above
* Click **Next...**
* Save API key

### Configure Deep Security Smart Check

Open Web console and go to **Users**. Click **+ CREATE** button.
Create new user with auditor role.

**Note**: regular administrator account can be used,
though this is less secure.

### Configure vulrem CronJob

Edit vulrem_secrets.yaml file:
 ```yaml
apiVersion: v1
kind: Secret
metadata:
  name: vulremsecrets
type: Opaque
stringData:
    SMARTCHECK_USERNAME: "<Name of Smart Check user with auditor role>"
    SMARTCHECK_PASSWORD: "<Password of this user>"
    DEEPSECURITY_API_KEY: "<Deep Security API key>"
```

Provide appropriate values for following variables:
* SMARTCHECK_USERNAME
* SMARTCHECK_PASSWORD
* DEEPSECURITY_API_KEY

Edit vulrem_cronjob.yaml file:
```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: VulRem
spec:
  schedule: "0 1 * * *" # Run once a day at 1 a.m.
  jobTemplate:
    spec:
      template:
        spec:
          replicas: 1
          restartPolicy: OnFailure
          containers:
            - name: "VulRem"
              image: "mpkondrashin/vulrem:0.1"
              imagePullPolicy: Always
          env:
            - name: DEEPSECURITY_POLICY_ID
              value: "<Policy ID>"
            - name: DEEPSECURITY_URL
              value: "https://<DSM address>:4119/api"
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

Provide appropriate values for following variables:
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

### Test VulRem

To test vulrem run following command:
```shell
$ kubectl create job --from=cronjob/vulrem vulrem-test
```

To check vulrem logs use following command:
```shell
$ kubectl logs jobs/vulrem-test
```

### VulRem in action

After successful completion of policy configuration,
vulrem makes two changes to chosen policy:
* Apropriate Intrusion Prevention module filters are turned on
* Description is populated with list of CVEs that present in one
of container images, but can not be covered by any of 
  Deep Security IPS rules
  
## P.S. Running VulRem not in K8s
Preparation step for Deep Security and Smart Check are the same.
### Running as separate script

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
DEEP_SECURITY_API_KEY=<API key>
DEEPSECURITY_POLICY_ID=<Policy ID>
```
Run container using following command:
```
$ docker run --env env.list mpkondrashin/vulrem
```
or 
```
$ docker run --env env.list vulrem
```
if your have built container from source.