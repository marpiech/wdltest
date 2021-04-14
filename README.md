# wdltest

Wdltest is python3 package to test wdl workflows. It requires java JDK to run Cromwell.

## How to install
```
pip3 install --upgrade --index-url https://test.pypi.org/simple/ --no-deps wdltest==0.0.10
```

## How to run
```
wdltest -t test.json
```

## How to configure
```
{
    "wdl":"${ROOTDIR}/src/main/wdl/modules/panel-hpo/panel-hpo.wdl",
    "threads": 1,
    "tests": [
        {
            "name":"Primary test",
            "bcoCheck": true,
            "stdoutCheck": true,
            "inputs": {
              "panel_hpo.hpo_terms": "HP:0001679, HP:0007018. HP:0000722, HP:0000256",
              "panel_hpo.genes": "HTT",
              "panel_hpo.diseases": "Osteogenesis imperfecta, Ehlers-Danlos",
              "panel_hpo.sample_id": "test",
              "panel_hpo.panel_names": ["ACMG_Incidental_Findings", "COVID-19_research", "Cancer_Germline", "Cardiovascular_disorders"],
              "panel_hpo.phenotypes_description": "Increased height, disproportionately long limbs and digits, anterior chest deformity, mild to moderate joint laxity, vertebral column deformity (scoliosis and thoracic lordosis), and a narrow, highly arched palate with crowding of the teeth are frequent skeletal features"
            },
            "conditions": [
            ]
        },
        {
            "name":"Primary test",
            "inputs": {
              "panel_hpo.hpo_terms": "HP:0001679, HP:0007018. HP:0000722, HP:0000256",
              "panel_hpo.genes": "HTT",
              "panel_hpo.diseases": "Osteogenesis imperfecta, Ehlers-Danlos",
              "panel_hpo.sample_id": "test",
              "panel_hpo.panel_names": ["ACMG_Incidental_Findings", "COVID-19_research", "Cancer_Germline", "Cardiovascular_disorders"],
              "panel_hpo.phenotypes_description": "Increased height, disproportionately long limbs and digits, anterior chest deformity, mild to moderate joint laxity, vertebral column deformity (scoliosis and thoracic lordosis), and a narrow, highly arched palate with crowding of the teeth are frequent skeletal features"
            },
            "conditions": [
                {
                    "file":"bco",
                    "name":"Bco exists",
                    "error_message":"Bco does not exist",
                    "command":"echo $file"
                },
                {
                    "file":"bco",
                    "name":"Provenance domain exists and is not empty",
                    "error_message":"Provenance domain not found in bco or is empty",
                    "command":"grep -q -m1 provenance_domain $file && jq -e 'if (.provenance_domain | length) == 0 then false else true end' $file"
                },
                {
                    "file":"bco",
                    "name":"Execution domain exists and is not empty",
                    "error_message":"Execution domain not found in bco or is empty",
                    "command":"grep -q -m1 execution_domain $file && jq -e 'if (.execution_domain | length) == 0 then false else true end' $file"
                },
                {
                    "file":"bco",
                    "name":"Parametric domain exists and is not empty",
                    "error_message":"Parametric domain not found in bco or is empty",
                    "command":"grep -q -m1 parametric_domain $file && jq -e 'if (.parametric_domain | length) == 0 then false else true end' $file"
                },
                {
                    "file":"bco",
                    "name":"Description domain exists and is not empty",
                    "warning":"true",
                    "command":"grep -q -m1 descripcion_domain $file && jq -e 'if (.description_domain | length) == 0 then false else true end' $file"
                },
                {
                    "file":"stdout_log",
                    "name":"Stdout exits",
                    "command":"test -f $file"
                },
                {
                    "file":"stdout_log",
                    "name":"Stdout exits",
                    "command":"test -f r$file"
                }

            ]
        }

    ]
}
```

## development
### test
```
ROOTDIR="/home/marpiech/workflows" python3 setup.py nosetests -s
```
### build
```
python3 setup.py sdist bdist_wheel
```
### upload
```
twine upload --repository testpypi dist/wdltest-1.0.0*
twine upload --repository pypi dist/wdltest-1.0.0*
```
### install
```
pip3 install --upgrade --no-deps wdltest==1.0.6
```
### kill cromwells
```
ps aux | grep Dweb | cut -d " " -f 2 | xargs kill -9
ps aux | grep Dweb
```
## Versions
### 0.0.10
Added return code 1 on failure
