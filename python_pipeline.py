import pendulum
from pynwb import NWBHDF5IO
from pynwb.file import Subject
from simply_nwb import SimpleNWB
from simply_nwb.pipeline import NWBSession
from simply_nwb.pipeline.enrichments.saccades import PutativeSaccadesEnrichment
from simply_nwb.pipeline.enrichments.saccades.predict_gui import PredictedSaccadeGUIEnrichment



def main():
    # Get the filenames for the timestamps.txt and dlc CSV
    prefix = "data/"

    dlc_filepath = f"20230420_unitME_session001_rightCam-0000DLC_resnet50_GazerMay24shuffle1_1030000.csv"
    timestamp_filepath = f"20230420_unitME_session001_rightCam_timestamps.txt"

    # Create a NWB file to put our data into
    print("Creating base NWB..")
    nwbfile = create_nwb()
    SimpleNWB.write(nwbfile, "base.nwb")
    del nwbfile

    # Load our newly created 'base' NWB and put in the 'putative' saccades (what we think *might* be a saccade)
    print("Enriching with putative NWB..")
    fp = NWBHDF5IO("base.nwb", "r")
    nwbfile = fp.read()

    enrichment = PutativeSaccadesEnrichment.from_raw(nwbfile, dlc_filepath, timestamp_filepath)
    SimpleNWB.write(nwbfile, "dlcdata.nwb")
    del nwbfile

    sess = NWBSession("dlcdata.nwb")  # Save to file
    sess.enrich(enrichment)
    sess.save("putative.nwb")  # Save to file
    del sess

    sess = NWBSession("putative.nwb")
    # Take our putative saccades and do the actual prediction for the start, end time, and time location
    print("Adding predictive data..")
    enrich = PredictedSaccadeGUIEnrichment(200, ["putative.nwb"])
    sess.enrich(enrich)
    print("Saving to NWB")
    sess.save("my_session_fulldata.nwb")  # Save as our finalized session, ready for analysis
    tw = 2


if __name__ == "__main__":
    main()
