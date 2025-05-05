import toml, argparse
from akbo import Account, run_pipeline

cli = argparse.ArgumentParser()
cli.add_argument("-r", "--recovery", action="store_true",
                 help="마지막 다운로드한 악보를 무시하고 전부 다시 다운로드")
cli.add_argument("-b", "--batch", type=int, default=100,
                 help="한 번에 발급 및 다운로드할 악보의 수")
cli.add_argument("-w", "--workers", type=int, default=10,
                 help="동시 비동기 요청 수")
args = cli.parse_args()

with open("config.toml", "r") as f:
    conf = toml.load(f)

out = conf["download"]["outdir"]

for acc in conf["accounts"]:
    run_pipeline(Account(acc["id"], acc["pw"]), outdir=out, workers=args.workers, recovery=args.recovery, batch=args.batch)