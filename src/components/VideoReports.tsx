import React, { useState, useEffect } from 'react';
import { Video, Play, Download, Calendar, TrendingUp, Clock } from 'lucide-react';

interface VideoReportsProps {
  user: any;
}

interface VideoReport {
  id: string;
  title: string;
  description: string;
  video_url: string;
  thumbnail_url: string;
  duration: number;
  created_at: string;
  report_type: string;
}

const VideoReports: React.FC<VideoReportsProps> = ({ user }) => {
  const [reports, setReports] = useState<VideoReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedReport, setSelectedReport] = useState<VideoReport | null>(null);

  useEffect(() => {
    fetchReports();
  }, [user]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      // Mock data for demo
      const mockReports: VideoReport[] = [
        {
          id: '1',
          title: 'Daily Productivity Report - January 16',
          description: 'Your personalized daily summary with achievements and upcoming priorities',
          video_url: 'https://example.com/video1.mp4',
          thumbnail_url: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=225&fit=crop',
          duration: 45,
          created_at: '2024-01-16T18:00:00Z',
          report_type: 'daily'
        },
        {
          id: '2',
          title: 'Weekly Summary - Week of January 8',
          description: 'Comprehensive weekly overview of your productivity and accomplishments',
          video_url: 'https://example.com/video2.mp4',
          thumbnail_url: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=225&fit=crop',
          duration: 72,
          created_at: '2024-01-14T17:00:00Z',
          report_type: 'weekly'
        },
        {
          id: '3',
          title: 'Motivational Boost - Keep Going!',
          description: 'Encouraging message based on your recent achievements and goals',
          video_url: 'https://example.com/video3.mp4',
          thumbnail_url: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=225&fit=crop',
          duration: 28,
          created_at: '2024-01-12T09:00:00Z',
          report_type: 'motivational'
        }
      ];

      setReports(mockReports);
    } catch (error) {
      console.error('Error fetching video reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (reportType: string) => {
    setGenerating(true);
    try {
      const response = await fetch('/api/video-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          report_type: reportType
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add new report to the list
        const newReport: VideoReport = {
          id: Date.now().toString(),
          title: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report - ${new Date().toLocaleDateString()}`,
          description: 'Your personalized AI-generated video report',
          video_url: data.video_url,
          thumbnail_url: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=225&fit=crop',
          duration: 45,
          created_at: new Date().toISOString(),
          report_type: reportType
        };

        setReports(prev => [newReport, ...prev]);
      } else {
        throw new Error('Failed to generate video report');
      }
    } catch (error) {
      console.error('Error generating video report:', error);
      alert('Failed to generate video report. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getReportTypeIcon = (type: string) => {
    switch (type) {
      case 'daily':
        return <Calendar className="h-4 w-4" />;
      case 'weekly':
        return <TrendingUp className="h-4 w-4" />;
      case 'motivational':
        return <Clock className="h-4 w-4" />;
      default:
        return <Video className="h-4 w-4" />;
    }
  };

  const getReportTypeColor = (type: string) => {
    switch (type) {
      case 'daily':
        return 'bg-blue-100 text-blue-800';
      case 'weekly':
        return 'bg-green-100 text-green-800';
      case 'motivational':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Video Reports</h2>
        <p className="text-gray-600">AI-generated personalized video summaries powered by Tavus</p>
      </div>

      {/* Generate New Report */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Generate New Report</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => generateReport('daily')}
            disabled={generating}
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Calendar className="h-8 w-8 text-blue-600 mb-2" />
            <h4 className="font-medium text-gray-900">Daily Report</h4>
            <p className="text-sm text-gray-600">Today's achievements and priorities</p>
          </button>
          
          <button
            onClick={() => generateReport('weekly')}
            disabled={generating}
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <TrendingUp className="h-8 w-8 text-green-600 mb-2" />
            <h4 className="font-medium text-gray-900">Weekly Summary</h4>
            <p className="text-sm text-gray-600">Comprehensive weekly overview</p>
          </button>
          
          <button
            onClick={() => generateReport('motivational')}
            disabled={generating}
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Clock className="h-8 w-8 text-purple-600 mb-2" />
            <h4 className="font-medium text-gray-900">Motivational Boost</h4>
            <p className="text-sm text-gray-600">Encouraging productivity message</p>
          </button>
        </div>
        
        {generating && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              <span className="text-blue-800">Generating your personalized video report...</span>
            </div>
            <p className="text-sm text-blue-600 mt-2">This usually takes 2-3 minutes</p>
          </div>
        )}
      </div>

      {/* Video Reports List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Your Video Reports</h3>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading video reports...</p>
          </div>
        ) : reports.length === 0 ? (
          <div className="p-8 text-center">
            <Video className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No video reports yet</h3>
            <p className="text-gray-600">Generate your first personalized video report above!</p>
          </div>
        ) : (
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {reports.map((report) => (
                <div
                  key={report.id}
                  className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
                >
                  {/* Thumbnail */}
                  <div className="relative">
                    <img
                      src={report.thumbnail_url}
                      alt={report.title}
                      className="w-full h-40 object-cover"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => setSelectedReport(report)}
                        className="bg-white bg-opacity-90 rounded-full p-3 hover:bg-opacity-100 transition-all"
                      >
                        <Play className="h-6 w-6 text-gray-900" />
                      </button>
                    </div>
                    <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                      {formatDuration(report.duration)}
                    </div>
                  </div>
                  
                  {/* Content */}
                  <div className="p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getReportTypeColor(report.report_type)}`}>
                        {getReportTypeIcon(report.report_type)}
                        <span>{report.report_type}</span>
                      </span>
                    </div>
                    
                    <h4 className="font-medium text-gray-900 mb-1">{report.title}</h4>
                    <p className="text-sm text-gray-600 mb-3">{report.description}</p>
                    
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>{new Date(report.created_at).toLocaleDateString()}</span>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setSelectedReport(report)}
                          className="text-indigo-600 hover:text-indigo-800"
                        >
                          Watch
                        </button>
                        <button className="text-gray-600 hover:text-gray-800">
                          <Download className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Video Player Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg overflow-hidden max-w-4xl w-full mx-4">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">{selectedReport.title}</h3>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="aspect-video bg-gray-900 flex items-center justify-center">
              {/* In a real implementation, this would be an actual video player */}
              <div className="text-center text-white">
                <Video className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">Video Player</p>
                <p className="text-sm opacity-75">
                  In a real implementation, this would play the video from: {selectedReport.video_url}
                </p>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Close Preview
                </button>
              </div>
            </div>
            
            <div className="p-4">
              <p className="text-gray-600">{selectedReport.description}</p>
              <div className="flex justify-between items-center mt-4 text-sm text-gray-500">
                <span>Duration: {formatDuration(selectedReport.duration)}</span>
                <span>Created: {new Date(selectedReport.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Technical Info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Video className="h-4 w-4" />
          <span>Powered by Tavus AI Video Generation • Personalized AI Avatars</span>
        </div>
      </div>
    </div>
  );
};

export default VideoReports;