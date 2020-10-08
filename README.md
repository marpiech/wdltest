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
    "wdl":"${ROOTDIR}/src/main/wdl/tasks/vcf-filter-freq/vcf-filter-freq.wdl",
    "tests": [
        {
            "name":"Primary test",
            "inputs": {
                "vcf_filter_freq_workflow.vcf_filter_freq.vcf_gz": "${ROOTDIR}/src/test/resources/data/vcf/chr15.282-chr15_47497301-49497301.annotated-with-frequencies.vcf.gz",
                "vcf_filter_freq_workflow.vcf_filter_freq.vcf_gz_tbi": "${ROOTDIR}/src/test/resources/data/vcf/chr15.282-chr15_47497301-49497301.annotated-with-frequencies.vcf.gz.tbi",
                "vcf_filter_freq_workflow.vcf_filter_freq.vcf_basename": "282-chr15_47497301-49497301"
            },
            "conditions": [
                {
                    "name":"Provenance domain exists",
                    "file":"bco",
                    "error_message":"Provenance domain not found in bco",
                    "command":"cat $file | grep -q provenance_domain"
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
twine upload --repository testpypi dist/wdltest-0.0.5*
```
### install
```
pip3 install --upgrade --index-url https://test.pypi.org/simple/ --no-deps wdltest==0.0.5
```

## Versions
### 0.0.10
Added return code 1 on failure