"use client"

import { useState } from "react"
import { ChevronDown, ChevronRight, Bot, FileText, Code, Lightbulb, TrendingUp } from "lucide-react"
import { cn } from "@/lib/utils"
import { motion, AnimatePresence } from "motion/react"

interface CollapsibleSectionProps {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
  defaultOpen?: boolean
}

function CollapsibleSection({ title, icon, children, defaultOpen = false }: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="border border-black/10 dark:border-white/10 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
      >
        <div className="flex items-center gap-3">
          {icon}
          <span className="font-medium text-black dark:text-white">{title}</span>
        </div>
        <motion.div
          animate={{ rotate: isOpen ? 90 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronRight className="w-4 h-4 text-black/60 dark:text-white/60" />
        </motion.div>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="p-4 bg-white/50 dark:bg-black/20 border-t border-black/10 dark:border-white/10">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function ResponsePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-black dark:text-white mb-2">
            Analysis Complete
          </h1>
          <p className="text-black/60 dark:text-white/60">
            Here's what I found based on your request
          </p>
        </div>

        {/* Main Content */}
        <div className="space-y-4">
          <CollapsibleSection 
            title="Summary" 
            icon={<FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />}
            defaultOpen={true}
          >
            <div className="space-y-3">
              <p className="text-black/80 dark:text-white/80 leading-relaxed">
                Based on your input, I've analyzed the key components and identified several important patterns. 
                The data suggests a strong correlation between the variables you mentioned, with particular 
                emphasis on the temporal aspects of the system.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="bg-blue-50 dark:bg-blue-950/30 p-3 rounded-lg">
                  <div className="text-sm font-medium text-blue-700 dark:text-blue-300">Confidence</div>
                  <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">94%</div>
                </div>
                <div className="bg-green-50 dark:bg-green-950/30 p-3 rounded-lg">
                  <div className="text-sm font-medium text-green-700 dark:text-green-300">Accuracy</div>
                  <div className="text-2xl font-bold text-green-900 dark:text-green-100">87%</div>
                </div>
                <div className="bg-purple-50 dark:bg-purple-950/30 p-3 rounded-lg">
                  <div className="text-sm font-medium text-purple-700 dark:text-purple-300">Relevance</div>
                  <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">92%</div>
                </div>
              </div>
            </div>
          </CollapsibleSection>

          <CollapsibleSection 
            title="Technical Details" 
            icon={<Code className="w-5 h-5 text-green-600 dark:text-green-400" />}
          >
            <div className="space-y-4">
              <div className="bg-gray-50 dark:bg-gray-900/50 p-4 rounded-lg">
                <h4 className="font-medium text-black dark:text-white mb-2">Algorithm Performance</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-black/60 dark:text-white/60">Processing Time:</span>
                    <span className="text-black dark:text-white">2.3 seconds</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-black/60 dark:text-white/60">Memory Usage:</span>
                    <span className="text-black dark:text-white">156 MB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-black/60 dark:text-white/60">CPU Utilization:</span>
                    <span className="text-black dark:text-white">23%</span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-900/50 p-4 rounded-lg">
                <h4 className="font-medium text-black dark:text-white mb-2">Data Points Analyzed</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-black/60 dark:text-white/60">Total Records</div>
                    <div className="font-medium text-black dark:text-white">1,247</div>
                  </div>
                  <div>
                    <div className="text-black/60 dark:text-white/60">Valid Entries</div>
                    <div className="font-medium text-black dark:text-white">1,189</div>
                  </div>
                  <div>
                    <div className="text-black/60 dark:text-white/60">Outliers Detected</div>
                    <div className="font-medium text-black dark:text-white">23</div>
                  </div>
                  <div>
                    <div className="text-black/60 dark:text-white/60">Patterns Found</div>
                    <div className="font-medium text-black dark:text-white">7</div>
                  </div>
                </div>
              </div>
            </div>
          </CollapsibleSection>

          <CollapsibleSection 
            title="Insights & Recommendations" 
            icon={<Lightbulb className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />}
          >
            <div className="space-y-4">
              <div className="border-l-4 border-yellow-500 pl-4">
                <h4 className="font-medium text-black dark:text-white mb-2">Key Insights</h4>
                <ul className="space-y-2 text-sm text-black/80 dark:text-white/80">
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span>Peak performance occurs during morning hours (9-11 AM)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span>User engagement drops significantly on weekends</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span>Mobile usage has increased by 34% in the last quarter</span>
                  </li>
                </ul>
              </div>
              <div className="border-l-4 border-blue-500 pl-4">
                <h4 className="font-medium text-black dark:text-white mb-2">Recommendations</h4>
                <ul className="space-y-2 text-sm text-black/80 dark:text-white/80">
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span>Optimize server resources for morning traffic spikes</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span>Implement weekend-specific features to boost engagement</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span>Prioritize mobile-first design improvements</span>
                  </li>
                </ul>
              </div>
            </div>
          </CollapsibleSection>

          <CollapsibleSection 
            title="Trends & Analytics" 
            icon={<TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />}
          >
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30 p-4 rounded-lg">
                  <h4 className="font-medium text-black dark:text-white mb-3">Growth Metrics</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-black/60 dark:text-white/60">Monthly Active Users</span>
                      <span className="text-sm font-medium text-green-600 dark:text-green-400">+12.5%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-black/60 dark:text-white/60">Session Duration</span>
                      <span className="text-sm font-medium text-green-600 dark:text-green-400">+8.3%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-black/60 dark:text-white/60">Conversion Rate</span>
                      <span className="text-sm font-medium text-red-600 dark:text-red-400">-2.1%</span>
                    </div>
                  </div>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30 p-4 rounded-lg">
                  <h4 className="font-medium text-black dark:text-white mb-3">Performance Indicators</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-black/60 dark:text-white/60">Load Time</span>
                      <span className="text-sm font-medium text-green-600 dark:text-green-400">-15.2%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-black/60 dark:text-white/60">Error Rate</span>
                      <span className="text-sm font-medium text-green-600 dark:text-green-400">-5.8%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-black/60 dark:text-white/60">Uptime</span>
                      <span className="text-sm font-medium text-green-600 dark:text-green-400">99.7%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CollapsibleSection>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <button 
            onClick={() => window.history.back()}
            className="inline-flex items-center gap-2 px-6 py-3 bg-black/10 dark:bg-white/10 hover:bg-black/20 dark:hover:bg-white/20 rounded-lg transition-colors text-black dark:text-white"
          >
            <ChevronRight className="w-4 h-4 rotate-180" />
            Back to Prompt
          </button>
        </div>
      </div>
    </div>
  )
} 