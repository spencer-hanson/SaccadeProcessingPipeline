import glob
import os
import uuid

import pendulum
from pynwb import NWBHDF5IO
from pynwb.file import Subject
from simply_nwb import SimpleNWB
from simply_nwb.pipeline import NWBSession
from simply_nwb.pipeline.enrichments.saccades import PutativeSaccadesEnrichment


def create_nwb(foldername):
    # desc = open(os.path.join(foldername, "experiment_description.txt")).read()

    # Create the NWB file, TODO Put data in here about mouse and experiment
    nwbfile = SimpleNWB.create_nwb(
        # Required
        session_description="Mouse cookie eating session",
        # Subtract 1 year so we don't run into the 'NWB start time is at a greater date than current' issue
        session_start_time=pendulum.now().subtract(years=1),
        experimenter=["Schmoe, Joe"],
        lab="Felsen Lab",
        experiment_description="Gave a mouse a cookie",
        # Optional
        identifier="cookie_0",
        subject=Subject(**{
            "subject_id": "1",
            "age": "P90D",  # ISO-8601 for 90 days duration
            "strain": "TypeOfMouseGoesHere",  # If no specific used, 'Wild Strain'
            "description": "Mouse#2 idk",
            "sex": "M",  # M - Male, F - Female, U - unknown, O - other
            # NCBI Taxonomy link or Latin Binomial (e.g.'Rattus norvegicus')
            "species": "http://purl.obolibrary.org/obo/NCBITaxon_10116",
        }),
        session_id="session0",
        institution="CU Anschutz",
        keywords=["mouse"],
        # related_publications="DOI::LINK GOES HERE FOR RELATED PUBLICATIONS"
    )
    return nwbfile


def search_for_data(prefix):
    datafolder = os.listdir(prefix)
    print(f"Found {len(datafolder)} files in {prefix}")
    datafiles = {}

    for folder in datafolder:
        if os.path.isdir(os.path.join(prefix, folder)):
            found_ts = glob.glob(os.path.join(prefix, folder, "*timestamps*.txt"))
            found_csv = glob.glob(os.path.join(prefix, folder, "*.csv"))
            if len(found_ts) == 0:
                raise ValueError("Can't find any files matching '*timestamps*.txt in folder!")
            if len(found_csv) == 0:
                raise ValueError("Can't find any files matching '*csv.txt in folder!")
            ts_fn = found_ts[0]
            csv_fn = found_csv[0]
            datafiles[folder] = {"timestamps": ts_fn, "csv": csv_fn}
            tw = 2
    return datafiles


def process_folder(foldername, data, prefix, outputdir):
    print(f"Processing '{foldername}'")
    tmp_dir = os.path.join("tmpdir", str(uuid.uuid4()))

    if not os.path.exists("tmpdir"):
        os.mkdir("tmpdir")

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    dlc_filepath = data["csv"]
    timestamp_filepath = data["timestamps"]

    print("Creating base NWB..")
    nwbfile = create_nwb(os.path.join(prefix, foldername))
    SimpleNWB.write(nwbfile, os.path.join(tmp_dir, "tmp_base.nwb"))
    del nwbfile

    # Load our newly created 'base' NWB and put in the 'putative' saccades (what we think *might* be a saccade)
    print("Enriching with putative NWB..")
    fp = NWBHDF5IO(os.path.join(tmp_dir, "tmp_base.nwb"), "r")
    nwbfile = fp.read()

    enrichment = PutativeSaccadesEnrichment.from_raw(nwbfile, dlc_filepath, timestamp_filepath)
    SimpleNWB.write(nwbfile, os.path.join(tmp_dir, "tmp_dlcdata.nwb"))
    del nwbfile

    sess = NWBSession(os.path.join(tmp_dir, "tmp_dlcdata.nwb"))  # Save to file
    sess.enrich(enrichment)
    sess.save(os.path.join(outputdir, f"{foldername}_putative.nwb"))  # Save to file
    del sess
    fp.close()

def main():
    prefix = "data/"  # TODO Change me to dir of sessions
    outputdir = "putative_output"

    datafiles = search_for_data(prefix)
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    for foldername, data in datafiles.items():
        process_folder(foldername, data, prefix, outputdir)

    tw = 2


if __name__ == "__main__":
    main()

