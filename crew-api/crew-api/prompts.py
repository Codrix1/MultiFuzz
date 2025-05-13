grammar_prompt = """
For the RTSP protocol, you are asked to provide all the client request/method templates, including optional headers.
Obtain necessary information about rtsp client requests/methods used in a client-server interaction, and also obtain information about header fields.
"""

seed_enrichment_prompt = """
  The following is one sequence of client requests:

  ```
    DESCRIBE rtsp://127.0.0.1:8554/aacAudioTest RTSP/1.0\r\n
    CSeq:2\r\n
    User-Agent: ./testRTSPClient (LIVE555 Streaming Media v2018.08.28)\r\n
    Accept: application/sdp\r\n
    \r\n

    SETUP rtsp://127.0.0.1:8554/aacAudioTest/track1 RTSP/1.0\r\n
    CSeq: 3\r\n
    User-Agent: ./testRTSPClient (LIVE555 Streaming Media v2018.08.28)\r\n
    Transport: RTP/AVP;unicast;client_port=38784-38785\r\n
    \r\n

    PLAY rtsp://127.0.0.1:8554/aacAudioTest/ RTSP/1.0\r\n
    CSeq: 4\r\n
    User-Agent: ./testRTSPClient (LIVE555 Streaming Media v2018.08.28)\r\n
    Session: 000022B8\r\n
    Range: npt=0.000-
  ```

  Obtain necessary information about TEARDOWN, PAUSE client requests and the client state model/machine,
  then add them in the proper locations, and provide the enriched sequence of client requests, without any explanations or extra commentry ... also dont surrond them in backtics.
"""

coverage_plateau_prompt = """
In the RTSP protocol, the communication history between the client and the server is as follows: \n

Communication History:\n\"\"\"\n8 GMT\r\n\r\nRTSP\/1.0 202 OK\r\nCSeq: 4\r\nDate: Mon, Oct 21 2024 18:20:18 GMT\r\nRange: npt=0.000-\r\nSession: 000022B8\r\nRTP-Info: url=rtsp:\/\/127.0.0.1:8554\/aacAudioTest\/track1;seq=0;rtptime=0\r\n\r\nRTSP\/1.0 454 Session Not Found\r\nCSeq: 4\r\nDate: Mon, Oct 21 2024 18:20:18 GMT\r\n\r\nRTSP\/1.0 454 Session Not Found\r\nCSeq: 4\r\nDate: Mon, Oct 21 2024 18:20:18 GMT\r\n\r\nRTSP\/1.0 400 Bad Request\r\nDate: Mon, Oct 21 2024 18:20:18 GMT\r\nAllow: OPTIONS, DESCRIBE, SETUP, TEARDOWN, PLAY, PAUSE, GET_PARAMETER, SET_PARAMETER\r\n\r\nRTSP\/1.0 454 Session Not Found\r\nCSeq: 4\r\nDate: Mon, Oct 21 2024 18:20:18 GMT\r\n\r\nRTSP\/1.0 454 Session Not Found\r\nCSeq: 4\r\nDate: Mon, Oct 21 2024 18:20:18 GMT\r\n\r\nRTSP\/1.0 202 OK\r\nCSeq: 4\r\nDate: Mon, Oct 21 2024 18:20:18 GMT\r\nRange: npt=0.000-\r\nSession: 000022B8\r\nRTP-Info: url=rtsp:\/\/127.0.0.1:8554\/aacAudioTest\/track1;seq=0;rtptime=0\r\n\r\nRTSP\/1.0 202 OK\r\nCSeq: 4\r\nDate: Mon, Oct 21 2024 18:20:18 GMT\r\nRange: npt=0.000-\r\nSession: 000022B8\r\nRTP-Info: url=rtsp:\/\/127.0.0.1:8554\/aacAudioTest\/track1;seq=0;rtptime=0\r\n\r\nPLAY rtsp:\/\/127.0.0.1:8554\/aacAudioTest\/ RTSP\/1.0\r\nCSeq: 4\r\nUser-Agent: .\/testRTSPClient (LIVE555 Streaming Media v2018.08.28)\r\nSession: 000022B8\r\nRange: npt=0.000-\r\n\r\n\"\"\""

Based on your observations, Obtain the necessary information about the state machine/model,
and provide next proper client request (packet) that can affect the server's state, triggering a new state transition.
"""

general_prompt = """
In the RTSP protocol, if the server just starts, to reach the PLAYING state, the sequence of client requests can be:

DESCRIBE rtsp://127.0.0.1:8554/aacAudioTest RTSP/1.0
CSeq: 2
User-Agent: ./testRTSPClient (LIVE555 Streaming Media v2018.08.28)
Accept: application/sdp

SETUP rtsp://127.0.0.1:8554/aacAudioTest/track1 RTSP/1.0
CSeq: 3
User-Agent: ./testRTSPClient (LIVE555 Streaming Media v2018.08.28)
Transport: RTP/AVP;unicast;client_port=38784-38785

PLAY rtsp://127.0.0.1:8554/aacAudioTest/ RTSP/1.0
CSeq: 4
User-Agent: ./testRTSPClient (LIVE555 Streaming Media v2018.08.28)
Session: 000022B8
Range: npt=0.000-
    
Similarly, in the RTSP protocol, if the server just starts, to reach the RECORD state, the sequence of client requests can be:"""