import public_meetings

meetings = public_meetings.load_meetings()

# from docs:
# meeting['final']['doc'][i]['text']      # text of the i-th document segment
# meeting['final']['doc'][i]['id']        # id of the i-th document segment

# meeting['final']['ctm'][j]['text']      # text of the j-th transcription segment
# meeting['final']['ctm'][j]['id']        # id of the j-th transcription segment
# meeting['final']['ctm'][j]['aligned']   # doc segment id corresponding to the j-th transcription segment

# show one meeting (via for loop and break method since its not a  simple list)
for meeting in meetings:
    print(meetings[meeting])
    break   