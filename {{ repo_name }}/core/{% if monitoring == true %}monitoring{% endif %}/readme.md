# How to run monitoring locally
Install the monitoring-core, the version is matched, example:
```terminal
pip install monitoring-lib==0.0.4
```
Local direct runner
```terminal
cd <repo_name>/<repo_name>/core/
python -m monitoring.runner --local
```
Local docker runner
```terminal
cd <repo_name>/<repo_name>/core/
python -m monitoring.runner --docker
```
Dataproc runner (on gitlab runner)
```terminal
cd <repo_name>/<repo_name>/core/
python -m monitoring.runner
```

Please refer the link - https://mobius-wiki.bt.com/display/DI/Monitoring+Library   for details on monitoring library