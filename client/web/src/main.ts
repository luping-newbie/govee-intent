// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

import { Player } from "./player.ts";
import { Recorder } from "./recorder.ts";
import "./style.css";
import { LowLevelRTClient } from "rt-client";
import { REALTIME_API_URL, AUTH_API_URL } from "./config.ts";
import axios from 'axios';

let realtimeStreaming: LowLevelRTClient;
let audioRecorder: Recorder;
let audioPlayer: Player;
let userToken: string;

async function initial(){
  const endpoint = REALTIME_API_URL + userToken;
  realtimeStreaming = new LowLevelRTClient(new URL(endpoint));

  if (audioPlayer) {
    audioPlayer.clear();
  }
  audioPlayer = new Player();
  audioPlayer.init(24000);

  makeNewTextBlock("<< Session Started >>");
  makeNewTextBlock();
  await Promise.all([resetAudio(false), handleRealtimeMessages()]);
}

async function start_realtime() {
  // remove config message due to this message will be sent by middle tier
  // try {
  //   console.log("sending session config");
  //   await realtimeStreaming.send(createConfigMessage());
  // } catch (error) {
  //   console.log(error);
  //   makeNewTextBlock("[Connection error]: Unable to send initial config message. Please check your endpoint and authentication details.");
  //   setFormInputState(InputState.ReadyToStart);
  //   return;
  // }
  // console.log("sent");
  // await Promise.all([resetAudio(true), handleRealtimeMessages()]);
  resetAudio(true);
}

// function createConfigMessage(): SessionUpdateMessage {

//   let configMessage: SessionUpdateMessage = {
//     type: "session.update",
//     session: {
//       turn_detection: {
//         type: "server_vad",
//       },
//       input_audio_transcription: {
//         model: "whisper-1"
//       }
//     }
//   };

//   return configMessage;
// }

// Asynchronous function to handle real-time messages
async function handleRealtimeMessages() {
  // Loop through each message from the real-time streaming
  for await (const message of realtimeStreaming.messages()) {
    // Initialize a console log with the message type
    let consoleLog = "" + message.type;

    // Switch case to handle different message types
    switch (message.type) {
      case "control":
        // If the action is 'text_done', append a horizontal rule to the form container
        if(message.action == "text_done"){
          formReceivedTextContainer.appendChild(document.createElement("hr"));
        // If the action is 'speech_started', create a new text block and clear the audio player
        }else if(message.action == "speech_started"){
          makeNewTextBlock("<< Speech Started >>");
          let textElements = formReceivedTextContainer.children;
          latestInputSpeechBlock = textElements[textElements.length - 1];
          makeNewTextBlock();
          audioPlayer.clear();
        }
        break;
      case "text_delta":
        // Append the delta text to the current text block
        appendToTextBlock(message.delta);
        break;
      case "audio_delta":
        // Play response audio
        const binary = atob(message.delta);
        const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
        const pcmData = new Int16Array(bytes.buffer);
        audioPlayer.play(pcmData);
        break;
      case "transcription":
        // Shown user request's transcription
        latestInputSpeechBlock.textContent += " User: " + message.text;
        break;
      default:
        consoleLog = JSON.stringify(message, null, 2);
        break
    }
    if (consoleLog) {
      console.log(consoleLog);
    }
  }
  resetAudio(false);
}

/**
 * Basic audio handling
 */

let recordingActive: boolean = false;
let buffer: Uint8Array = new Uint8Array();

function combineArray(newData: Uint8Array) {
  const newBuffer = new Uint8Array(buffer.length + newData.length);
  newBuffer.set(buffer);
  newBuffer.set(newData, buffer.length);
  buffer = newBuffer;
}

function processAudioRecordingBuffer(data: Buffer) {
  const uint8Array = new Uint8Array(data);
  combineArray(uint8Array);
  if (buffer.length >= 4800) {
    const toSend = new Uint8Array(buffer.slice(0, 4800));
    buffer = new Uint8Array(buffer.slice(4800));
    const regularArray = String.fromCharCode(...toSend);
    const base64 = btoa(regularArray);
    if (recordingActive) {
      realtimeStreaming.send({
        bytes: base64,
      });
    }
  }

}

async function resetAudio(startRecording: boolean) {
  recordingActive = false;
  if (audioRecorder) {
    audioRecorder.stop();
  }

  audioRecorder = new Recorder(processAudioRecordingBuffer);

  if (startRecording) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioRecorder.start(stream);
    recordingActive = true;
  }
}

/**
 * UI and controls
 */

const formReceivedTextContainer = document.querySelector<HTMLDivElement>(
  "#received-text-container",
)!;
const formAuthenticateButton =
  document.querySelector<HTMLButtonElement>("#authenticate")!;
const formUseridField =
  document.querySelector<HTMLInputElement>("#userid")!;
const formStartButton =
  document.querySelector<HTMLButtonElement>("#start-recording")!;
const formStopButton =
  document.querySelector<HTMLButtonElement>("#stop-recording")!;
const formClearAllButton =
  document.querySelector<HTMLButtonElement>("#clear-all")!;
const formUserMessageField =
  document.querySelector<HTMLTextAreaElement>("#user-message-area")!;
const formSendButton =
  document.querySelector<HTMLButtonElement>("#send-message")!;
let latestInputSpeechBlock: Element;

enum InputState {
  WaitAuthenticate,
  Working,
  ReadyToStart,
  ReadyToStop,
}

function setFormInputState(state: InputState) {
  formAuthenticateButton.disabled = state != InputState.WaitAuthenticate;
  formUseridField.disabled = state != InputState.WaitAuthenticate;
  formStartButton.disabled = state != InputState.ReadyToStart;
  formStopButton.disabled = state != InputState.ReadyToStop;
  formSendButton.disabled = state != InputState.ReadyToStart;
  formUserMessageField.disabled = state != InputState.ReadyToStart;
}

function makeNewTextBlock(text: string = "") {
  let newElement = document.createElement("p");
  newElement.textContent = text;
  formReceivedTextContainer.appendChild(newElement);
}

function appendToTextBlock(text: string) {
  let textElements = formReceivedTextContainer.children;
  if (textElements.length == 0) {
    makeNewTextBlock();
  }
  textElements[textElements.length - 1].textContent += text;
}

formStartButton.addEventListener("click", async () => {
  setFormInputState(InputState.Working);

  try {
    start_realtime();
    setFormInputState(InputState.ReadyToStop);
  } catch (error) {
    console.log(error);
    setFormInputState(InputState.ReadyToStart);
  }
});

formStopButton.addEventListener("click", async () => {
  setFormInputState(InputState.Working);
  resetAudio(false);
  // realtimeStreaming.close();
  setFormInputState(InputState.ReadyToStart);
});

formClearAllButton.addEventListener("click", async () => {
  formReceivedTextContainer.innerHTML = "";
});

formAuthenticateButton.addEventListener("click", async () => {
  setFormInputState(InputState.Working);
  const userid = formUseridField.value;
  if (!userid) {
    setFormInputState(InputState.WaitAuthenticate);
    return;
  }
  makeNewTextBlock(`Authenticating ${userid}...`);
  try {
    const response = await axios.post(AUTH_API_URL + userid, {});
    userToken = response.data.user_key;
    makeNewTextBlock("Authenticated successfully.");
    makeNewTextBlock(`User token: ${userToken}`);
  } catch (error) {
    console.error('Error:', error);
  }

  initial();
  setFormInputState(InputState.ReadyToStart);
});

formSendButton.addEventListener("click", async () => {
  setFormInputState(InputState.Working);

  const userMessage = formUserMessageField.value;
  makeNewTextBlock(`User : ${userMessage}`);
  makeNewTextBlock();
  realtimeStreaming.send({
    text: userMessage,
  });
  setFormInputState(InputState.ReadyToStart);
});