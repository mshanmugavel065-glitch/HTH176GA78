import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, X, Sparkles } from 'lucide-react';
import { uploadDataset } from '../services/api';

export default function DatasetUpload({ onUploadComplete, metadata }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;

    const fileExt = file.name.split('.').pop().toLowerCase();
    if (fileExt !== 'csv' && fileExt !== 'json') {
      setUploadError('Unsupported file format. Please upload a CSV or JSON file.');
      return;
    }

    setUploadError('');
    setIsUploading(true);
    try {
      const newState = await uploadDataset(file);
      if (onUploadComplete) onUploadComplete(newState);
      setIsOpen(false);
    } catch (err) {
      setUploadError(err.response?.data?.detail || 'Failed to parse disaster dataset file.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  return (
    <div>
      {/* Upload Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/40 text-cyan-300 hover:text-white text-xs font-mono font-semibold transition-all cursor-pointer shadow-sm shadow-cyan-500/10"
      >
        <UploadCloud className="w-4 h-4 text-cyan-400" />
        📁 UPLOAD DISASTER DATASET
      </button>

      {/* Modal Dialog */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-5 relative">
            
            <button
              onClick={() => setIsOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="space-y-1">
              <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
                <UploadCloud className="w-5 h-5 text-cyan-400" />
                Upload Disaster Measurement Dataset
              </h3>
              <p className="text-xs text-slate-400">
                Upload custom CSV or JSON telemetry containing rainfall, flood level, affected area, or medical casualty data.
              </p>
            </div>

            {/* Drag and Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3 ${
                dragActive
                  ? 'border-cyan-400 bg-cyan-500/10'
                  : 'border-slate-700 hover:border-slate-600 bg-slate-950/50 hover:bg-slate-950'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv, .json"
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                className="hidden"
              />

              <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                <FileText className="w-6 h-6 text-cyan-400" />
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-200">
                  {isUploading ? 'Parsing dataset & evaluating indicators...' : 'Drop your CSV or JSON file here'}
                </p>
                <p className="text-xs text-slate-500 mt-1 font-mono">
                  Supported formats: .CSV, .JSON (e.g. location, rainfall_mm, flood_level_m, injured, road_access)
                </p>
              </div>
            </div>

            {/* Error Banner */}
            {uploadError && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{uploadError}</span>
              </div>
            )}

            {/* Metadata Preview if Dataset Loaded */}
            {metadata && metadata.filename && (
              <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs font-mono space-y-2">
                <div className="flex items-center justify-between text-slate-300">
                  <span className="flex items-center gap-1.5 font-semibold text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" /> Active Dataset: {metadata.filename}
                  </span>
                  <span className="text-slate-400">{metadata.row_count} Sectors</span>
                </div>
                {metadata.columns_detected && (
                  <p className="text-[11px] text-slate-400">
                    <strong className="text-slate-300">Indicators detected:</strong> {metadata.columns_detected.join(', ')}
                  </p>
                )}
                {metadata.warnings && metadata.warnings.length > 0 && (
                  <p className="text-[11px] text-amber-400 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    {metadata.warnings[0]}
                  </p>
                )}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-semibold cursor-pointer"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
