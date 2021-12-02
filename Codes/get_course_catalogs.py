from pathlib import Path
from bs4 import BeautifulSoup
import requests
import time
import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial

def get_term_names(start, end):
    return [str(int(i/3)) + "0" + str((int(i) % 3) + 1) for i in range(start*3, end*3)]


def get_term_subjects(term):
    return [option.get("value") for option in BeautifulSoup(requests.post(
        "https://suis.sabanciuniv.edu/prod/bwckctlg.p_disp_cat_term_date",
        {
            "call_proc_in": "bwckctlg.p_disp_dyn_ctlg",
            "cat_term_in": term
        }
    ).content, "html.parser").find("select", attrs={"name": "sel_subj"}).find_all("option")]


def get_term_catalog(term):
    return requests.post(
        "https://suis.sabanciuniv.edu/prod/bwckctlg.p_display_courses",
        {
            "term_in": term,
            "call_proc_in": "bwckctlg.p_disp_dyn_ctlg",
            "sel_crse_start": "",
            "sel_crse_end": "",
            "sel_title": "",
            "sel_levl": "",
            "sel_schd": "",
            "sel_coll": "",
            "sel_divs": "",
            "sel_dept": "",
            "sel_to_cred": "",
            "sel_from_cred": "",
            "sel_attr": "",
            "sel_subj": ["dummy"] + get_term_subjects(term),
        }).content


def get_and_save(term):
    print("starting", term)
    chrono = time.perf_counter()
    catalog = get_term_catalog(term)
    print("got", term, "in", str(time.perf_counter() - chrono), "seconds")

    path = Path(__file__).parent / "../Catalogs/Raws" / (term + ".html")
    with path.open(mode="wb+") as f:
        f.write(catalog)

        return True


async def main():
    with ProcessPoolExecutor(3) as pool:
        loop = asyncio.get_running_loop()
        runners = [loop.run_in_executor(pool, partial(get_and_save, term)) for term in get_term_names(int(input("start year: ")), int(input("end year (excluded): ")))]
        crs = asyncio.gather(*runners)


if __name__ == "__main__":
    asyncio.run(main())
