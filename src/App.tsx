import React, { useState, useEffect } from 'react';
import { MessageCircle, Calendar, CheckSquare, Brain, Mic, Video, Settings } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import TaskManager from './components/TaskManager';
import CalendarView from './components/CalendarView';
import Dashboard from './components/Dashboard';
import VoiceInterface from './components/VoiceInterface';
import VideoReports from './components/VideoReports';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Initialize user session
    const initUser = async () => {
      // In a real app, this would check for existing auth
      const mockUser = {
        id: 'demo-user-123',
        name: 'Demo User',
        email: 'demo@flowmind.ai'
      };
      setUser(mockUser);
    };

    initUser();
  }, []);

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Brain },
    { id: 'chat', label: 'Chat', icon: MessageCircle },
    { id: 'tasks', label: 'Tasks', icon: CheckSquare },
    { id: 'calendar', label: 'Calendar', icon: Calendar },
    { id: 'voice', label: 'Voice', icon: Mic },
    { id: 'video', label: 'Video Reports', icon: Video },
  ];

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard user={user} />;
      case 'chat':
        return <ChatInterface user={user} />;
      case 'tasks':
        return <TaskManager user={user} />;
      case 'calendar':
        return <CalendarView user={user} />;
      case 'voice':
        return <VoiceInterface user={user} />;
      case 'video':
        return <VideoReports user={user} />;
      default:
        return <Dashboard user={user} />;
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Loading FlowMind AI...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-indigo-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">FlowMind AI</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user.name}</span>
              <Settings className="h-5 w-5 text-gray-400 cursor-pointer hover:text-gray-600" />
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation */}
        <nav className="w-64 bg-white shadow-sm min-h-screen">
          <div className="p-4">
            <ul className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <li key={tab.id}>
                    <button
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                        activeTab === tab.id
                          ? 'bg-indigo-100 text-indigo-700 border-r-2 border-indigo-600'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="h-5 w-5 mr-3" />
                      {tab.label}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {renderActiveTab()}
        </main>
      </div>
    </div>
  );
}

export default App;