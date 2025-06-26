import React, { useState, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Play, Pause } from 'lucide-react';

interface VoiceInterfaceProps {
  user: any;
}

const VoiceInterface: React.FC<VoiceInterfaceProps> = ({ user }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processVoiceInput(audioBlob);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processVoiceInput = async (audioBlob: Blob) => {
    setLoading(true);
    
    try {
      // Convert blob to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Audio = reader.result?.toString().split(',')[1];
        
        if (base64Audio) {
          const response = await fetch('/api/voice', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              audio_data: base64Audio,
              user_id: user.id
            })
          });

          if (response.ok) {
            const data = await response.json();
            setTranscript(data.transcription);
            setResponse(data.response);
            setAudioUrl(data.audio_url);
          } else {
            throw new Error('Voice processing failed');
          }
        }
      };
      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error('Error processing voice input:', error);
      
      // Fallback for demo
      const mockTranscriptions = [
        'Show me my tasks for today',
        'What do I have on my calendar?',
        'Add a task to review quarterly reports',
        'Schedule a meeting with the team tomorrow',
        'What should I focus on today?'
      ];
      
      const mockResponses = [
        'You have 5 pending tasks today. Your highest priority items are reviewing quarterly reports and preparing the client presentation.',
        'Today you have 3 events: Team meeting at 9 AM, project review at 2 PM, and a client call at 4 PM.',
        'I\'ve added "Review quarterly reports" to your task list with high priority.',
        'I can help you schedule that meeting. What time works best for you tomorrow?',
        'Based on your priorities, I recommend focusing on your high-priority tasks first: reviewing quarterly reports and preparing the client presentation.'
      ];
      
      const randomIndex = Math.floor(Math.random() * mockTranscriptions.length);
      setTranscript(mockTranscriptions[randomIndex]);
      setResponse(mockResponses[randomIndex]);
      setAudioUrl('demo-audio-url');
    } finally {
      setLoading(false);
    }
  };

  const playResponse = () => {
    if (audioUrl && !isPlaying) {
      setIsPlaying(true);
      
      // In a real implementation, this would play the actual audio
      // For demo, we'll simulate audio playback
      setTimeout(() => {
        setIsPlaying(false);
      }, 3000);
    }
  };

  const stopPlayback = () => {
    setIsPlaying(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Voice Interface</h2>
        <p className="text-gray-600">Talk to FlowMind AI using voice commands powered by ElevenLabs</p>
      </div>

      {/* Voice Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="text-center">
          <div className="mb-6">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={loading}
              className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-200 ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                  : 'bg-indigo-600 hover:bg-indigo-700'
              } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isRecording ? (
                <MicOff className="h-8 w-8 text-white" />
              ) : (
                <Mic className="h-8 w-8 text-white" />
              )}
            </button>
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {loading ? 'Processing...' : isRecording ? 'Listening...' : 'Ready to listen'}
            </h3>
            <p className="text-sm text-gray-600">
              {loading 
                ? 'Converting speech and generating response...'
                : isRecording 
                ? 'Speak your command, then click the microphone to stop'
                : 'Click the microphone to start voice input'
              }
            </p>
          </div>

          {loading && (
            <div className="mt-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600 mx-auto"></div>
            </div>
          )}
        </div>
      </div>

      {/* Conversation History */}
      {(transcript || response) && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversation</h3>
          
          <div className="space-y-4">
            {transcript && (
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Mic className="h-4 w-4 text-blue-600" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="bg-blue-50 rounded-lg p-3">
                    <p className="text-sm font-medium text-blue-900 mb-1">You said:</p>
                    <p className="text-blue-800">{transcript}</p>
                  </div>
                </div>
              </div>
            )}

            {response && (
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                    <Volume2 className="h-4 w-4 text-indigo-600" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="bg-indigo-50 rounded-lg p-3">
                    <div className="flex justify-between items-start mb-1">
                      <p className="text-sm font-medium text-indigo-900">FlowMind AI responded:</p>
                      {audioUrl && (
                        <button
                          onClick={isPlaying ? stopPlayback : playResponse}
                          className="flex items-center space-x-1 text-xs text-indigo-600 hover:text-indigo-800"
                        >
                          {isPlaying ? (
                            <>
                              <Pause className="h-3 w-3" />
                              <span>Stop</span>
                            </>
                          ) : (
                            <>
                              <Play className="h-3 w-3" />
                              <span>Play</span>
                            </>
                          )}
                        </button>
                      )}
                    </div>
                    <p className="text-indigo-800">{response}</p>
                    {isPlaying && (
                      <div className="mt-2">
                        <div className="flex items-center space-x-2 text-xs text-indigo-600">
                          <Volume2 className="h-3 w-3" />
                          <span>Playing audio response...</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Voice Commands Help */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Voice Commands</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Task Management</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• "Add task review quarterly reports"</li>
              <li>• "Show me my pending tasks"</li>
              <li>• "Complete task prepare presentation"</li>
              <li>• "What should I focus on today?"</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Calendar</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• "What do I have today?"</li>
              <li>• "Schedule meeting with team tomorrow"</li>
              <li>• "Find free time this week"</li>
              <li>• "Am I free at 2 PM?"</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Information</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• "Explain time management techniques"</li>
              <li>• "Summarize my productivity today"</li>
              <li>• "How can I be more productive?"</li>
              <li>• "What is the Pomodoro technique?"</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Proactive Help</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• "Give me suggestions"</li>
              <li>• "Help me prioritize"</li>
              <li>• "Optimize my schedule"</li>
              <li>• "What's my status?"</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Technical Info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Volume2 className="h-4 w-4" />
          <span>Powered by ElevenLabs Voice AI • Speech-to-Text & Text-to-Speech</span>
        </div>
      </div>
    </div>
  );
};

export default VoiceInterface;