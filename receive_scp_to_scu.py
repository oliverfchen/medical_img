#!/usr/bin/env python
# coding: utf-8



import os
import storescu 
from pydicom.filewriter import write_file_meta_info  #renames file 
from pydicom.uid import ImplicitVRLittleEndian,JPEG2000Lossless, JPEGLossless
#from pynetdicom import AE
#from pynetdicom.presentation import _build_context
from pynetdicom.sop_class import CTImageStorage
from pynetdicom import (
    AE, debug_logger, evt,
    AllStoragePresentationContexts,
    ALL_TRANSFER_SYNTAXES
)
from pynetdicom.sop_class import CTImageStorage,VerificationSOPClass
#debug_logger()
'''def handle_store(event):
    """Handle EVT_C_STORE events."""
    ds = event.dataset
    ds.file_meta = event.file_meta
    ds.save_as(ds.SOPInstanceUID, write_like_original=False)

    return 0x0000'''

def handle_store(event, storage_dir):
     
     """Handle EVT_C_STORE events."""
     try:
         os.makedirs(storage_dir, exist_ok=True)
     except:
         # Unable to create output dir, return failure status
         return 0xC001
     #file = str("oliver^test")+".dcm"
     file = str(event.request.AffectedSOPInstanceUID) #+".dcm"
     # We rely on the UID from the C-STORE request instead of decoding
     fname = os.path.join(storage_dir, file)
     with open(fname, 'wb') as f:
         # Write the preamble, prefix and file meta information elements
         f.write(b'\x00' * 128)
         f.write(b'DICM')
         write_file_meta_info(f, event.file_meta)
         # Write the raw encoded dataset
         f.write(event.request.DataSet.getvalue())
    
     #print ("patient Name = " , event.dataset.PatientName)
     #newfile = str(event.dataset.PatientName)[:-1]+str(event.request.AffectedSOPInstanceUID.split('.')[-1])+".dcm"
     #newfile = '{0!s}-{1!s}-{2!s}'.format(dataset.SOPInstanceUID, dataset.SeriesInstanceUID, dataset.InstanceNumber) + '.dcm'
     #newfName = os.path.join(storage_dir, newfile)
     #os.rename(fname, newfName )
         
     host = "192.168.8.177"
     port = "4242"
     arg0 = '-ds'      #-ds all files under dir, '' single file
     arg1 = '-q'       #--v verbose  q quick, d debug
     arg2 = '-cx'      #require context
     
     file = fname
     storescu.main([arg0,host,port,file,arg1,arg2])
     print ("file send!",file)
     os.remove(file)
     return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store, ['out'])]
#context_a = _build_context(CTImageStorage, JPEGLossless)
#context_b = _build_context(CTImageStorage, JPEG2000Lossless)
ae = AE()
#ae.add_requested_context(context_a)
#ae.add_requested_context(context_b)
storage_sop_classes = [
     cx.abstract_syntax for cx in AllStoragePresentationContexts
 ]+ [JPEGLossless]+ [JPEG2000Lossless] +[VerificationSOPClass]+[CTImageStorage]+[VerificationSOPClass]


for uid in storage_sop_classes:
     ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)
n=0        
#ae.add_supported_context(CTImageStorage, VerificationSOPClass)
ae.start_server(('', 11112), block=True, evt_handlers=handlers)




