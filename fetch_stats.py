import click
import httpx
import json
import pathlib
import time


@click.command()
@click.argument(
    "stats_file",
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.argument("packages", nargs=-1)
@click.option("--sleep", type=float)
@click.option("-v", "--verbose", is_flag=True)
def cli(stats_file, packages, sleep, verbose):
    "Fetch latest PyPI stats for these packages and write them disk"
    path = pathlib.Path(stats_file)
    data = {}
    for package in packages:
        url = "https://pypistats.org/api/packages/{}/overall?mirrors=true".format(
            package
        )
        response = httpx.get(url)
        if response.status_code == 404:
            click.echo("Got 404 for {}".format(package), err=True)
            continue
        response.raise_for_status()
        raw_stats = response.json()["data"]
        # Re-arrange into date: number dictionary
        data[package] = {rs["date"]: rs["downloads"] for rs in raw_stats}
        if verbose:
            print("Fetched {}, {} days".format(package, len(data[package])))
        if sleep:
            time.sleep(sleep)
    path.write_text(json.dumps(data, indent=4, sort_keys=True))


if __name__ == "__main__":
    cli()
