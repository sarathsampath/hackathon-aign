import * as TranscribeClient from "./transcribe-lib";

let finalTranscribe = [];

const selectedLanguage = "en-US";
let isStartRecording = true;
const diagnosisURL =
  "https://y2druc0yvk.execute-api.us-east-1.amazonaws.com/dev/diagnosis";

const clusterURL = "http://3.236.189.236:5000/analytics";

console.log("Transcribe script loaded");

window.makeDiagnosis = async () => {
  const response = await fetch(diagnosisURL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      chat: finalTranscribe,
    }),
  });
  const data = await response.json();
  document.getElementById(
    "outputSummary"
  ).innerHTML = `Summary: ${data.body.summary}`;
  document.getElementById(
    "outputDiagnosis"
  ).innerHTML = `Diagnosis: ${data.body.diagnosis}`;
  await fetch(clusterURL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      patientId: "1",
      symptoms:
        typeof data.body.symptoms == "string"
          ? [data.body.symptoms]
          : data.body.symptoms,
    }),
  });
  finalTranscribe = [];
};

window.onRecordPress = () => {
  console.log("Recording started " + isStartRecording);
  try {
    if (isStartRecording) {
      startRecording();
    } else {
      stopRecording();
    }
  } catch (e) {
    console.error("Error in onRecordPress", e);
  }
};

const clearTranscription = () => {
  document.getElementById("transcribedText").innerHTML = "";
};

const startRecording = async () => {
  clearTranscription();
  isStartRecording = false;
  try {
    await TranscribeClient.startRecording(
      selectedLanguage,
      onTranscriptionDataReceived
    );
  } catch (error) {
    alert("An error occurred while recording: " + error.message);
    stopRecording();
  }
};

const getSpeakerId = (data) => {
  for (const item of data.Alternatives[0].Items) {
    if (item.Speaker != undefined) {
      return item.Speaker + 1;
    }
  }
  return "";
};

const getTranscribedHtml = (speakerId, content) => {
  return `Speaker - ${speakerId} : ${content}`;
};

const onTranscriptionDataReceived = (data) => {
  const speakerId = getSpeakerId(data);
  document.getElementById("transcribedText").innerHTML = getTranscribedHtml(
    speakerId,
    data.Alternatives[0].Transcript
  );
  if (data.IsPartial == false) {
    finalTranscribe.push({
      speakerId,
      data: data.Alternatives[0].Transcript,
    });
  }
};

const stopRecording = function () {
  console.log(finalTranscribe);
  isStartRecording = true;
  TranscribeClient.stopRecording();
};
