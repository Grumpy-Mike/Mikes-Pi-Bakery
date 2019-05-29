import midi
midiPort = midi.MidiConnector('/dev/ttyAMA0')
#noteOff = midi.NoteOff(note_number,velocity)
noteOn = midi.NoteOn(63,40)

#noteOn.note_number = 60
#noteOn.velocity = 40
msg = midi.Message(noteOn,channel=1)

midiPort.write(msg)
