import pendulum
from pynwb import NWBHDF5IO
from pynwb.file import Subject
from simply_nwb import SimpleNWB
from simply_nwb.pipeline import NWBSession
from simply_nwb.pipeline.enrichments.saccades import PutativeSaccadesEnrichment
from simply_nwb.pipeline.enrichments.saccades.predict_gui import PredictedSaccadeGUIEnrichment


def main():
    sess = NWBSession("putative.nwb")
    # Take our putative saccades and do the actual prediction for the start, end time, and time location
    print("Adding predictive data..")
    enrich = PredictedSaccadeGUIEnrichment(200, ["putative.nwb"], 20)
    sess.enrich(enrich)
    print("Saving to NWB")
    sess.save("my_session_fulldata.nwb")  # Save as our finalized session, ready for analysis
    tw = 2


if __name__ == "__main__":
    main()
