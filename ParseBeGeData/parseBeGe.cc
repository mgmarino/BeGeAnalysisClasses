/* Code to parse out Soudan BeGe data.  Copyright, M.G. Marino, CENPA, University of Washington.*/

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include "MGTWaveform.hh"
#include "MGTEvent.hh"
#include "TFile.h"
#include "TTree.h"
#include <getopt.h>
#include <arpa/inet.h>
using namespace std;

static const char Usage[] =
"\n"
"Usage: [program] [binary_input_file] [output_root_file]\n"
"\n";

/* Swap buffer swaps along 32-bit boundaries. Uses
   ntohl for portability. */
void swap_buffer(char* buffer, size_t length)
{
    uint32_t* data_buffer = (uint32_t*) buffer;
    length /= sizeof(data_buffer[0]);
    for (size_t i=0;i<length;i++) {
        data_buffer[i] = ntohl(data_buffer[i]); 
    }
}

/* Reading the waveforms, 2 waveforms interlaced in a "column" format. */
char* read_waveforms(MGTWaveform& waveform_one, MGTWaveform& waveform_two, 
                    char* buffer, size_t length_of_waveforms)
{
  waveform_one.SetLength(length_of_waveforms);
  waveform_two.SetLength(length_of_waveforms);
  uint32_t* data_buffer = (uint32_t*) buffer;
  for (size_t i=0;i<waveform_one.GetLength();i++){
    // Data in the binary are raw IEEE float values.  
    // This casting allows them to be set in the native
    // MGTWaveform format (double)
    waveform_one[i] = *((float*) (data_buffer+2*i));  
    waveform_two[i] = *((float*) (data_buffer+2*i + 1));  
  }
  return buffer + 2*length_of_waveforms*sizeof(data_buffer[0]);
}

/* Reading the two pulser chunks and the datetime */
char* read_pulser_chunk_plus_datetime(UInt_t& pulser_chunk_one, UInt_t& pulser_chunk_two, 
                                      ULong64_t& datetime, char* buffer)
{
  uint32_t* data_buffer = (uint32_t*) buffer;
  double temp = ((double)(*((float*)data_buffer)));
  double temp2 = ((double)(*((float*)data_buffer+1))); 

  // Converting to ULong64_t
  datetime = (ULong64_t)(temp*1e7) + (ULong64_t)temp2; 
  pulser_chunk_one = data_buffer[2];
  pulser_chunk_two = data_buffer[3];
  return buffer + 4*sizeof(data_buffer[0]);
}

// Initialization for MGTEvent
void prepare_for_next_trigger(MGTEvent& event, 
                              vector<MGTWaveform*>& vector_of_waveforms, 
                              size_t num_waveforms,
                              double sampling_frequency) 
{
  vector_of_waveforms.clear(); 
  // We allocate waveforms in a defined location since we are using the TClonesArray of ROOT.
  for(size_t i=0;i<num_waveforms;i++) {
    // The following 'new' construction is to use space in the defined location.  See TClonesArray doc for details.
    vector_of_waveforms.push_back( new((*(event.GetWaveforms()))[i]) MGTWaveform(NULL, 0, sampling_frequency, 0.0, MGWaveform::kADC, 0));
  }
}

int main(int argc, char** argv)
{
  /* Define constants of the data record here. */
  // These should in principle be defined at runtime.
  const Double_t sampling_frequency = 20*CLHEP::MHz;
  const size_t waveform_length = 8000; 
  const size_t extra_bytes = 16;
  const size_t waveform_word_length = 4;
  const size_t num_waveforms_per_trigger = 6;
  const size_t trigger_event_size_in_bytes = waveform_word_length*num_waveforms_per_trigger*
                                             waveform_length + extra_bytes;

  char* data_buffer = new char[trigger_event_size_in_bytes];
  
  static struct option longOptions[] = {
  };

  // Following is for eventual extension to allowing command line options
  while(1) {
    char optId = getopt_long(argc, argv, "", longOptions, NULL);
    if(optId == -1) break;
    switch(optId) {
      default: // unrecognized option
        cout << Usage;
        return 1;
    }
  }

  // Output usage
  if (argc < optind + 2) {
    cout << Usage;
    return 1;
  }

  // Following are the files to process.  
  // Grab the input and output names from the command line
  string root_output_file_name = argv[optind+1];
  string binary_input_file_name = argv[optind];

  // Open binary input file
  ifstream binary_input_file(binary_input_file_name.c_str(), ios::in | ios::binary);

  // Perform sanity check, ensure that the data is not corrupted:
  size_t begin, end;
  begin = binary_input_file.tellg();
  binary_input_file.seekg(0, ios::end);
  end = binary_input_file.tellg();
  binary_input_file.seekg(0, ios::beg);

  size_t size_of_file = end - begin;
  if (size_of_file % trigger_event_size_in_bytes != 0) {
    cout << "File corrupted." << endl;
    return 1;
  }
  // End sanity check

  // Initialize ROOT output.
  // We store this output in MGTWaveforms within MGTEvents.
  MGTEvent* event = new MGTEvent(); 
  event->InitializeWaveforms(num_waveforms_per_trigger);
  vector<MGTWaveform*> vector_of_waveforms;
  UInt_t pulser_chunk_one;
  UInt_t pulser_chunk_two;
  ULong64_t datetime;

  TFile open_file(root_output_file_name.c_str(), "recreate");
  TTree tree("soudan_wf_analysis", "Soudan WF Tree");
  tree.Branch("EventBranch", "MGTEvent", &event); 
  tree.Branch("timestamp", &datetime, "timestamp/l");
  tree.Branch("pulser_chunk_one", &pulser_chunk_one, "pulser_chunk_one/i");
  tree.Branch("pulser_chunk_two", &pulser_chunk_two, "pulser_chunk_two/i");
  

  // Total number of events in the file
  size_t number_of_events = size_of_file/trigger_event_size_in_bytes;
  size_t number_read_out = 0;
  do {
    // Initialization
    prepare_for_next_trigger(*event, 
                             vector_of_waveforms, 
                             num_waveforms_per_trigger,
                             sampling_frequency);

    // Read in the next event
    binary_input_file.read(data_buffer, trigger_event_size_in_bytes);
    if (binary_input_file.eof()) {
        cout << "End of file reached prematurely?" << endl;
    }

    // Swap buffer to host machines endianness
    swap_buffer(data_buffer, trigger_event_size_in_bytes); 

    // Read the first two waveforms (chan 0, chan 1)
    char* next_read = read_waveforms(*vector_of_waveforms[0], *vector_of_waveforms[1], data_buffer, waveform_length);
    // Read the time and  
    next_read = read_pulser_chunk_plus_datetime(pulser_chunk_one, pulser_chunk_two, datetime, next_read); 
    // Read the next two waveforms, chan 2, muon veto
    next_read = read_waveforms(*vector_of_waveforms[2], *vector_of_waveforms[3], next_read, waveform_length);
    // Read the final two waveforms, raw preamp trace 1 and 2
    next_read = read_waveforms(*vector_of_waveforms[4], *vector_of_waveforms[5], next_read, waveform_length);

    // Fill the tree with this event.
    tree.Fill();

    // Peek forces the eof flag to be set if it encounters the end 
    // of the file,  The ensures a correct exit from this loop.
    binary_input_file.peek();
    number_read_out++;
  } while (!binary_input_file.eof());
  
  if (number_read_out != number_of_events) {
    cout << "Error reading file" << endl;
  } 
  tree.Write("", TObject::kOverwrite);

  return 0;
}

