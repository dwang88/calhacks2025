"use client";

import { AlertTriangle, Bug, CheckCircle, FileText, Info, ServerCrash, XCircle } from "lucide-react";

interface JsonDataViewerProps {
  data: any;
}

const KeyValueRow = ({ label, value }: { label: string, value: any }) => (
    <div className="flex items-start">
        <div className="font-semibold text-gray-700 w-28 flex-shrink-0">{label}:</div>
        <div className="text-gray-600 break-words min-w-0">{value}</div>
    </div>
);


const JsonDataViewer: React.FC<JsonDataViewerProps> = ({ data }) => {
  if (!data || typeof data !== 'object') {
    return (
        <pre className="bg-gray-100 text-gray-800 p-3 rounded-md text-xs font-mono overflow-x-auto whitespace-pre-wrap">
            {JSON.stringify(data, null, 2)}
        </pre>
    );
  }

  const { success, error, stderr, stdout, bugs, pagesVisited, duration } = data;

  const hasSuccessInfo = success !== undefined;
  const hasBugs = bugs && bugs.length > 0;

  return (
    <div className="text-xs space-y-4 font-sans">
        {hasSuccessInfo && (
             <div className={`flex items-center gap-2 p-2 rounded-md border ${success ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-700'}`}>
                {success ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                <span className="font-semibold">{success ? 'Operation Succeeded' : 'Operation Failed'}</span>
            </div>
        )}

        {error && (
            <div className="p-3 rounded-md bg-red-50 border border-red-200">
                <div className="flex items-center gap-2 text-red-700 font-semibold mb-1">
                    <AlertTriangle className="w-4 h-4" />
                    Error
                </div>
                <p className="text-red-600 font-mono">{error}</p>
            </div>
        )}

        {stderr && (
            <div>
                <h4 className="font-semibold text-gray-700 mb-1 flex items-center gap-1.5"><ServerCrash className="w-3.5 h-3.5"/> Stderr:</h4>
                <pre className="bg-gray-800 text-gray-300 p-3 rounded-md text-xs font-mono overflow-x-auto whitespace-pre-wrap">
                    {stderr}
                </pre>
            </div>
        )}

        {stdout && (
            <div>
                <h4 className="font-semibold text-gray-700 mb-1 flex items-center gap-1.5"><FileText className="w-3.5 h-3.5"/> Stdout:</h4>
                <pre className="bg-gray-100 text-gray-800 p-3 rounded-md text-xs font-mono overflow-x-auto whitespace-pre-wrap">
                    {stdout}
                </pre>
            </div>
        )}
        
        {(pagesVisited !== undefined || duration !== undefined) && (
             <div className="p-3 rounded-md bg-blue-50 border border-blue-200 space-y-2">
                 <h4 className="font-semibold text-blue-700 mb-1 flex items-center gap-1.5"><Info className="w-3.5 h-3.5"/> Crawl Summary:</h4>
                 <div className="grid grid-cols-2 gap-2 text-blue-600">
                    {pagesVisited !== undefined && <KeyValueRow label="Pages Visited" value={pagesVisited} />}
                    {duration !== undefined && <KeyValueRow label="Duration" value={`${duration}s`} />}
                 </div>
            </div>
        )}
        
        {hasBugs && (
            <div className="p-3 rounded-md bg-orange-50 border border-orange-200">
                <h4 className="font-semibold text-orange-700 mb-2 flex items-center gap-1.5"><Bug className="w-3.5 h-3.5"/> Bugs Found ({bugs.length}):</h4>
                <div className="space-y-2">
                    {bugs.map((bug: any, index: number) => (
                    <div key={index} className="text-orange-600 border-l-2 border-orange-200 pl-2">
                        <p><span className="font-semibold">{bug.type}:</span> {bug.issue}</p>
                        <p className="opacity-80">Page: {bug.page}</p>
                    </div>
                    ))}
                </div>
            </div>
        )}
    </div>
  );
};

export default JsonDataViewer; 