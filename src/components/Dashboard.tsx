import React, { useState, useEffect } from 'react';
import { Calendar, CheckSquare, Clock, TrendingUp, AlertCircle, Lightbulb } from 'lucide-react';

interface DashboardProps {
  user: any;
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const [stats, setStats] = useState({
    pendingTasks: 0,
    completedToday: 0,
    todayEvents: 0,
    urgentTasks: 0
  });
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch user stats
        const tasksResponse = await fetch(`/api/user/${user.id}/tasks`);
        const eventsResponse = await fetch(`/api/user/${user.id}/events`);
        
        // Mock data for demo
        setStats({
          pendingTasks: 8,
          completedToday: 3,
          todayEvents: 4,
          urgentTasks: 2
        });

        // Mock suggestions
        setSuggestions([
          {
            id: 1,
            type: 'schedule_task',
            title: 'Schedule high-priority task',
            description: 'You have a free slot at 2 PM to work on "Quarterly Report"',
            priority: 'high'
          },
          {
            id: 2,
            type: 'break_reminder',
            title: 'Take a break',
            description: 'You\'ve been working for 2 hours. Consider a 15-minute break.',
            priority: 'medium'
          },
          {
            id: 3,
            type: 'priority_review',
            title: 'Review task priorities',
            description: 'You have 5 high-priority tasks. Consider redistributing priorities.',
            priority: 'low'
          }
        ]);

        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setLoading(false);
      }
    };

    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const handleSuggestionAction = async (suggestionId: number, action: string) => {
    try {
      // In a real app, this would call the backend
      console.log(`Suggestion ${suggestionId} ${action}`);
      
      // Remove suggestion from list
      setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
    } catch (error) {
      console.error('Error handling suggestion:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">Good morning, {user.name}! 🌟</h2>
        <p className="text-indigo-100">Ready to make today productive? Here's your overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center">
            <CheckSquare className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending Tasks</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pendingTasks}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed Today</p>
              <p className="text-2xl font-bold text-gray-900">{stats.completedToday}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Calendar className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Today's Events</p>
              <p className="text-2xl font-bold text-gray-900">{stats.todayEvents}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center">
            <AlertCircle className="h-8 w-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Urgent Tasks</p>
              <p className="text-2xl font-bold text-gray-900">{stats.urgentTasks}</p>
            </div>
          </div>
        </div>
      </div>

      {/* MindFlow Suggestions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center">
            <Lightbulb className="h-6 w-6 text-yellow-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">MindFlow Suggestions</h3>
          </div>
          <p className="text-sm text-gray-600 mt-1">Proactive insights to optimize your productivity</p>
        </div>
        
        <div className="p-6">
          {suggestions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No suggestions at the moment. You're doing great! 🎉</p>
          ) : (
            <div className="space-y-4">
              {suggestions.map((suggestion) => (
                <div
                  key={suggestion.id}
                  className={`p-4 rounded-lg border-l-4 ${
                    suggestion.priority === 'high'
                      ? 'border-red-400 bg-red-50'
                      : suggestion.priority === 'medium'
                      ? 'border-yellow-400 bg-yellow-50'
                      : 'border-blue-400 bg-blue-50'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{suggestion.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{suggestion.description}</p>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => handleSuggestionAction(suggestion.id, 'accept')}
                        className="px-3 py-1 text-xs font-medium text-white bg-indigo-600 rounded hover:bg-indigo-700 transition-colors"
                      >
                        Accept
                      </button>
                      <button
                        onClick={() => handleSuggestionAction(suggestion.id, 'dismiss')}
                        className="px-3 py-1 text-xs font-medium text-gray-600 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <CheckSquare className="h-6 w-6 text-indigo-600 mb-2" />
            <h4 className="font-medium text-gray-900">Add Task</h4>
            <p className="text-sm text-gray-600">Create a new task quickly</p>
          </button>
          
          <button className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Calendar className="h-6 w-6 text-indigo-600 mb-2" />
            <h4 className="font-medium text-gray-900">Schedule Event</h4>
            <p className="text-sm text-gray-600">Add to your calendar</p>
          </button>
          
          <button className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Clock className="h-6 w-6 text-indigo-600 mb-2" />
            <h4 className="font-medium text-gray-900">Find Free Time</h4>
            <p className="text-sm text-gray-600">Discover available slots</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;