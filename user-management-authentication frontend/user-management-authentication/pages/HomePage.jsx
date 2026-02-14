import { Link } from 'react-router-dom'
import { 
  Code, 
  BookOpen, 
  Lightbulb, 
  BarChart2, 
  ArrowRight,
  CheckCircle,
  Zap,
  Users
} from 'lucide-react'

/**
 * Home Page
 * Landing page for the application
 */
function HomePage() {
  const features = [
    {
      icon: BookOpen,
      title: 'Micro-Lessons',
      description: 'Learn concepts in bite-sized lessons designed for beginners. Each lesson focuses on one concept at a time.'
    },
    {
      icon: Code,
      title: 'Hands-on Practice',
      description: 'Apply what you learn immediately with coding challenges. Our integrated editor lets you code right in the browser.'
    },
    {
      icon: Lightbulb,
      title: 'AI Guidance',
      description: 'Get intelligent hints that help you think through problems. Our AI never gives away solutions - it helps you learn.'
    },
    {
      icon: BarChart2,
      title: 'Track Progress',
      description: 'Monitor your learning journey with detailed statistics, streaks, and personalized recommendations.'
    }
  ]

  const tracks = [
    {
      icon: '☕',
      title: 'Java with DSA',
      description: 'Master Java programming and data structures',
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: '📊',
      title: 'Data Science',
      description: 'Learn Python for data analysis and visualization',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: '🤖',
      title: 'AI Engineer',
      description: 'Build AI/ML models and deep learning systems',
      color: 'from-purple-500 to-pink-500'
    }
  ]

  const mockRecommendations = [
    {
      title: 'Java: Sliding Window Warmup',
      difficulty: 'easy',
      track: 'Java with DSA',
      reason: 'Great next step after arrays and loops.'
    },
    {
      title: 'Data Science: Pandas Data Cleaning',
      difficulty: 'medium',
      track: 'Data Science',
      reason: 'Builds practical analysis workflow confidence.'
    },
    {
      title: 'AI Engineer: Prompt Evaluation Basics',
      difficulty: 'hard',
      track: 'AI Engineer',
      reason: 'Strengthens model quality and reliability skills.'
    }
  ]

  return (
    <div className="min-h-screen bg-dark-950">
      {/* Navigation */}
      <nav className="bg-dark-900/80 backdrop-blur-md border-b border-dark-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Code className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">CodePath AI</span>
            </Link>
            
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="text-dark-300 hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900/20 to-transparent" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
              Learn to Code with{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
                AI-Powered Guidance
              </span>
            </h1>
            <p className="text-xl text-dark-300 mb-8 max-w-2xl mx-auto">
              Master programming through interactive lessons, hands-on practice, 
              and intelligent hints that help you think - not just copy answers.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="px-8 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
              >
                Start Learning Free
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/login"
                className="px-8 py-3 bg-dark-800 hover:bg-dark-700 text-white rounded-lg font-medium transition-colors"
              >
                Sign In
              </Link>
            </div>
          </div>

          {/* Code Editor Preview */}
          <div className="mt-16 relative">
            <div className="bg-dark-900 rounded-xl border border-dark-700 overflow-hidden shadow-2xl">
              <div className="flex items-center gap-2 px-4 py-3 bg-dark-800 border-b border-dark-700">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="ml-4 text-dark-400 text-sm">problem.py</span>
              </div>
              <div className="p-6 font-mono text-sm">
                <pre className="text-dark-300">
                  <code>
{`def two_sum(nums, target):
    """Find two numbers that add up to target."""
    # Your code here
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []`}
                  </code>
                </pre>
              </div>
            </div>
            
            {/* AI Hint Bubble */}
            <div className="absolute -right-4 top-1/2 transform translate-x-1/4 -translate-y-1/2 hidden lg:block">
              <div className="bg-primary-600 rounded-xl p-4 max-w-xs shadow-lg animate-pulse-glow">
                <div className="flex items-start gap-3">
                  <Lightbulb className="w-5 h-5 text-white flex-shrink-0 mt-1" />
                  <p className="text-white text-sm">
                    Think about what data structure could help you look up values more efficiently...
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-dark-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">
              Everything You Need to Learn
            </h2>
            <p className="text-dark-300 max-w-2xl mx-auto">
              A complete learning platform designed specifically for beginners, 
              with features that help you build real programming skills.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-dark-800 rounded-xl p-6 border border-dark-700 hover:border-primary-500 transition-colors"
              >
                <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-primary-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-dark-400 text-sm">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Learning Tracks Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">
              Choose Your Path
            </h2>
            <p className="text-dark-300 max-w-2xl mx-auto">
              Select a learning track that matches your goals. 
              Each path is carefully designed to take you from beginner to proficient.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {tracks.map((track, index) => (
              <div
                key={index}
                className="bg-dark-800 rounded-xl overflow-hidden border border-dark-700 hover:border-dark-500 transition-all hover:-translate-y-1"
              >
                <div className={`h-2 bg-gradient-to-r ${track.color}`} />
                <div className="p-6">
                  <div className="text-4xl mb-4">{track.icon}</div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {track.title}
                  </h3>
                  <p className="text-dark-400 mb-4">
                    {track.description}
                  </p>
                  <ul className="space-y-2 text-sm text-dark-300">
                    <li className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      Structured curriculum
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      Hands-on projects
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      AI-guided learning
                    </li>
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Mock Recommendations Section */}
      <section className="py-20 bg-dark-900/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Recommended Next Challenges</h2>
              <p className="text-dark-300">Preview of personalized recommendations you get after sign in.</p>
            </div>
            <Link
              to="/register"
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
            >
              Unlock My Plan
            </Link>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {mockRecommendations.map((item, index) => (
              <div key={index} className="bg-dark-800 rounded-xl border border-dark-700 p-5">
                <p className="text-primary-400 text-xs uppercase tracking-wide mb-2">{item.track}</p>
                <h3 className="text-white font-semibold mb-3">{item.title}</h3>
                <div className="flex items-center gap-2 mb-3">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    item.difficulty === 'easy'
                      ? 'bg-green-500/20 text-green-400'
                      : item.difficulty === 'medium'
                        ? 'bg-yellow-500/20 text-yellow-400'
                        : 'bg-red-500/20 text-red-400'
                  }`}>
                    {item.difficulty}
                  </span>
                </div>
                <p className="text-dark-400 text-sm">{item.reason}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Philosophy Section */}
      <section className="py-20 bg-gradient-to-br from-primary-900/20 to-dark-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-white mb-6">
                AI That Teaches,{' '}
                <span className="text-primary-400">Not Cheats</span>
              </h2>
              <p className="text-dark-300 mb-6">
                Our AI mentor is designed with one goal: to help you become a better programmer. 
                It will never give you the answer directly. Instead, it guides you to discover solutions yourself.
              </p>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Conceptual explanations</p>
                    <p className="text-dark-400 text-sm">Understand the "why" behind each concept</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Guiding questions</p>
                    <p className="text-dark-400 text-sm">Think through problems step by step</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Error explanations</p>
                    <p className="text-dark-400 text-sm">Learn from mistakes without getting the fix</p>
                  </div>
                </li>
              </ul>
            </div>
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-700">
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <Zap className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-primary-600/20 rounded-lg p-3 flex-1">
                    <p className="text-primary-300 text-sm">
                      "Think about what happens when your loop reaches the last element. 
                      What index are you trying to access?"
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-dark-700 rounded-full flex items-center justify-center flex-shrink-0">
                    <Users className="w-4 h-4 text-dark-400" />
                  </div>
                  <div className="bg-dark-700 rounded-lg p-3 flex-1">
                    <p className="text-dark-300 text-sm">
                      "Oh! I'm accessing index i+1 when i is already at the last position!"
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <Zap className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-primary-600/20 rounded-lg p-3 flex-1">
                    <p className="text-primary-300 text-sm">
                      "Exactly! Now, how might you adjust your loop to avoid that?"
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Start Your Coding Journey?
          </h2>
          <p className="text-dark-300 mb-8 max-w-2xl mx-auto">
            Join thousands of beginners who are learning to code the right way. 
            No shortcuts, no copying - just real learning.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium text-lg transition-colors"
          >
            Get Started for Free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-dark-900 border-t border-dark-700 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Code className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-white">CodePath AI</span>
            </div>
            <p className="text-dark-400 text-sm">
              © 2026 CodePath AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default HomePage
