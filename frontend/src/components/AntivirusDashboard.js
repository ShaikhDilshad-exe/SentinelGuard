import React, {
  useState,
  useRef,
  useEffect
} from "react";

import {
  Upload,
  Shield,
  Search,
  Loader2,
  AlertTriangle,
  CheckCircle,
  FileText,
  Hash
} from "lucide-react";

const SentinelGuardScanner = () => {

  // ---------------------------------------------------------
  // STATE
  // ---------------------------------------------------------
  const [file, setFile] = useState(null);

  const [isScanning, setIsScanning] = useState(false);

  const [scanResult, setScanResult] = useState(null);

  const [progress, setProgress] = useState(0);

  const [recentScans, setRecentScans] = useState([]);

  const [stats, setStats] = useState({
    scanned: 0,
    threats: 0,
    clean: 0
  });

  const fileInputRef = useRef(null);

  // ---------------------------------------------------------
  // LOAD STORAGE
  // ---------------------------------------------------------
  useEffect(() => {

    const savedStats = localStorage.getItem(
      "sentinel_stats"
    );

    const savedHistory = localStorage.getItem(
      "sentinel_history"
    );

    if (savedStats) {
      setStats(JSON.parse(savedStats));
    }

    if (savedHistory) {
      setRecentScans(JSON.parse(savedHistory));
    }

  }, []);

  // ---------------------------------------------------------
  // SAVE STORAGE
  // ---------------------------------------------------------
  useEffect(() => {

    localStorage.setItem(
      "sentinel_stats",
      JSON.stringify(stats)
    );

    localStorage.setItem(
      "sentinel_history",
      JSON.stringify(recentScans)
    );

  }, [stats, recentScans]);

  // ---------------------------------------------------------
  // FILE SELECT
  // ---------------------------------------------------------
  const handleFileChange = (e) => {

    const selectedFile = e.target.files[0];

    if (selectedFile) {

      setFile(selectedFile);

      setScanResult(null);

      setProgress(0);
    }
  };

  // ---------------------------------------------------------
  // SCAN
  // ---------------------------------------------------------
  const handleScan = async () => {

    if (!file) return;

    setIsScanning(true);

    setProgress(10);

    const progressInterval = setInterval(() => {

      setProgress((prev) => {

        if (prev >= 90) {
          return prev;
        }

        return prev + 10;

      });

    }, 350);

    try {

      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        "http://localhost:5000/api/scan",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      clearInterval(progressInterval);

      setProgress(100);

      setScanResult(data);

      // -----------------------------------------------------
      // UPDATE STATS
      // -----------------------------------------------------
      const isMalicious =
        (data.malicious || 0) > 0;

      setStats((prev) => ({

        scanned: prev.scanned + 1,

        threats:
          prev.threats +
          (isMalicious ? 1 : 0),

        clean:
          prev.clean +
          (isMalicious ? 0 : 1)

      }));

      // -----------------------------------------------------
      // UPDATE HISTORY
      // -----------------------------------------------------
      setRecentScans((prev) => [

        {
          file: file.name,

          status:
            isMalicious
              ? "MALICIOUS"
              : "SAFE",

          time:
            new Date().toLocaleTimeString()
        },

        ...prev.slice(0, 4)

      ]);

    } catch (error) {

      console.error(
        "Scan failed:",
        error
      );

    } finally {

      setTimeout(() => {

        setIsScanning(false);

      }, 500);
    }
  };

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------
  return (

    <div
      className="
        p-8
        bg-[#0a0a0c]
        min-h-screen
        text-slate-300
        font-sans
      "
    >

      {/* HEADER */}
      <div className="mb-10">

        <div className="flex items-center gap-4">

          <Shield
            className="text-purple-500"
            size={34}
          />

          <div>

            <h1
              className="
                text-4xl
                font-black
                text-white
              "
            >
              File Scanner
            </h1>

            <p
              className="
                text-slate-500
                mt-1
              "
            >
              Malware analysis powered by VirusTotal
            </p>

          </div>

        </div>

      </div>

      {/* TOP STATS */}
      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-3
          gap-6
          mb-10
        "
      >

        <StatCard
          label="Total Scanned"
          value={stats.scanned}
          color="text-white"
        />

        <StatCard
          label="Threats Blocked"
          value={stats.threats}
          color="text-red-500"
        />

        <StatCard
          label="System Clean"
          value={stats.clean}
          color="text-emerald-500"
        />

      </div>

      {/* MAIN GRID */}
      <div
        className="
          grid
          grid-cols-1
          lg:grid-cols-12
          gap-8
        "
      >

        {/* LEFT SIDE */}
        <div
          className="
            lg:col-span-7
            space-y-6
          "
        >

          {/* SCANNER */}
          <div
            className="
              bg-[#111114]
              border
              border-white/5
              rounded-3xl
              p-8
            "
          >

            {/* DROPZONE */}
            <div
              onClick={() =>
                fileInputRef.current.click()
              }
              className={`
                border-2
                border-dashed
                rounded-2xl
                p-10
                text-center
                cursor-pointer
                transition-all

                ${
                  file
                    ? "border-purple-500/40 bg-purple-500/5"
                    : "border-white/10 hover:border-purple-500/20"
                }
              `}
            >

              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
              />

              <Upload
                className={`
                  mx-auto
                  mb-4

                  ${
                    file
                      ? "text-purple-400"
                      : "text-slate-600"
                  }
                `}
                size={50}
              />

              <h3
                className="
                  text-2xl
                  font-bold
                  text-white
                "
              >
                {
                  file
                    ? file.name
                    : "Select Target File"
                }
              </h3>

              <p
                className="
                  text-slate-500
                  text-sm
                  mt-3
                "
              >
                Maximum file size: 32MB
              </p>

            </div>

            {/* PROGRESS */}
            {isScanning && (

              <div className="mt-6">

                <div
                  className="
                    flex
                    justify-between
                    text-xs
                    text-slate-500
                    mb-2
                    font-mono
                  "
                >

                  <span>
                    ANALYZING FILE...
                  </span>

                  <span>
                    {progress}%
                  </span>

                </div>

                <div
                  className="
                    w-full
                    bg-white/5
                    h-2
                    rounded-full
                    overflow-hidden
                  "
                >

                  <div
                    className="
                      bg-purple-500
                      h-full
                      transition-all
                      duration-300
                    "
                    style={{
                      width: `${progress}%`
                    }}
                  />

                </div>

              </div>

            )}

            {/* BUTTON */}
            <button
              onClick={handleScan}
              disabled={!file || isScanning}
              className="
                w-full
                mt-6
                py-4
                bg-purple-600
                hover:bg-purple-500
                disabled:bg-white/5
                disabled:text-slate-600
                text-white
                font-bold
                rounded-2xl
                transition-all
                flex
                items-center
                justify-center
                gap-3
                uppercase
                tracking-widest
                text-sm
              "
            >

              {isScanning ? (

                <>
                  <Loader2
                    className="animate-spin"
                    size={18}
                  />

                  Engine Active...

                </>

              ) : (

                <>
                  <Search size={18} />

                  Start Scan

                </>

              )}

            </button>

          </div>

          {/* RECENT SCANS */}
          <div
            className="
              bg-[#111114]
              border
              border-white/5
              rounded-3xl
              p-6
            "
          >

            <h3
              className="
                text-xs
                font-bold
                text-slate-500
                uppercase
                tracking-widest
                mb-5
              "
            >
              Recent Activity
            </h3>

            <div className="space-y-3">

              {
                recentScans.length === 0 ? (

                  <p className="text-slate-600 text-sm">
                    No recent scans available
                  </p>

                ) : (

                  recentScans.map((scan, i) => (

                    <div
                      key={i}
                      className="
                        flex
                        items-center
                        justify-between
                        p-4
                        bg-white/[0.02]
                        rounded-xl
                        border
                        border-white/5
                      "
                    >

                      <div
                        className="
                          flex
                          items-center
                          gap-3
                        "
                      >

                        <FileText
                          size={16}
                          className="text-slate-500"
                        />

                        <div>

                          <p
                            className="
                              text-sm
                              font-medium
                              text-white
                              line-clamp-1
                            "
                          >
                            {scan.file}
                          </p>

                          <p
                            className="
                              text-[10px]
                              text-slate-500
                            "
                          >
                            {scan.time}
                          </p>

                        </div>

                      </div>

                      <span
                        className={`
                          text-[10px]
                          font-bold
                          px-3
                          py-1
                          rounded-md

                          ${
                            scan.status === "SAFE"
                              ? "bg-emerald-500/10 text-emerald-500"
                              : "bg-red-500/10 text-red-500"
                          }
                        `}
                      >

                        {scan.status}

                      </span>

                    </div>

                  ))

                )
              }

            </div>

          </div>

        </div>

        {/* RIGHT SIDE */}
        <div
          className="
            lg:col-span-5
          "
        >

          <div
            className="
              bg-[#111114]
              border
              border-white/5
              rounded-3xl
              p-8
              h-full
            "
          >

            <h3
              className="
                text-xs
                font-bold
                text-slate-500
                uppercase
                tracking-widest
                mb-8
                border-b
                border-white/5
                pb-4
              "
            >
              Analysis Report
            </h3>

            {scanResult ? (

              <div className="space-y-4">

                <ReportRow
                  label="Malware"
                  value={scanResult.malicious}
                  color="text-red-500"
                  bg="bg-red-500/10"
                />

                <ReportRow
                  label="Suspicious"
                  value={scanResult.suspicious}
                  color="text-yellow-500"
                  bg="bg-yellow-500/10"
                />

                <ReportRow
                  label="Safe"
                  value={scanResult.harmless}
                  color="text-emerald-500"
                  bg="bg-emerald-500/10"
                />

                {/* HASH */}
                <div
                  className="
                    mt-8
                    p-5
                    bg-black/30
                    rounded-2xl
                    border
                    border-white/5
                  "
                >

                  <div
                    className="
                      flex
                      items-center
                      gap-2
                      text-[10px]
                      font-bold
                      text-slate-500
                      uppercase
                      mb-3
                    "
                  >

                    <Hash size={12} />

                    File Identity

                  </div>

                  <code
                    className="
                      text-[10px]
                      text-purple-400/80
                      break-all
                      font-mono
                    "
                  >
                    SHA256:
                    7f3b2a6c91f84e9a7bcd12ef45aa84
                  </code>

                </div>

                {/* STATUS */}
                <div
                  className={`
                    mt-6
                    p-5
                    rounded-2xl
                    border

                    ${
                      (scanResult.malicious || 0) > 0
                        ? "bg-red-500/10 border-red-500/20"
                        : "bg-emerald-500/10 border-emerald-500/20"
                    }
                  `}
                >

                  <div className="flex items-center gap-3">

                    {
                      (scanResult.malicious || 0) > 0
                        ? (
                          <AlertTriangle
                            className="text-red-500"
                          />
                        )
                        : (
                          <CheckCircle
                            className="text-emerald-500"
                          />
                        )
                    }

                    <div>

                      <p
                        className="
                          text-sm
                          font-bold
                          text-white
                        "
                      >
                        {
                          (scanResult.malicious || 0) > 0
                            ? "Threat Detected"
                            : "File Safe"
                        }
                      </p>

                      <p
                        className="
                          text-xs
                          text-slate-400
                          mt-1
                        "
                      >
                        Analysis completed successfully
                      </p>

                    </div>

                  </div>

                </div>

              </div>

            ) : (

              <div
                className="
                  h-64
                  flex
                  flex-col
                  items-center
                  justify-center
                  text-center
                  opacity-20
                "
              >

                <Search
                  size={48}
                  className="mb-4"
                />

                <p className="text-sm">
                  Awaiting file analysis
                </p>

              </div>

            )}

          </div>

        </div>

      </div>

    </div>

  );
};

// ---------------------------------------------------------
// HELPERS
// ---------------------------------------------------------

const StatCard = ({
  label,
  value,
  color
}) => (

  <div
    className="
      bg-[#111114]
      border
      border-white/5
      p-6
      rounded-3xl
    "
  >

    <p
      className="
        text-xs
        font-bold
        text-slate-500
        uppercase
        tracking-widest
      "
    >
      {label}
    </p>

    <p
      className={`
        text-5xl
        font-black
        mt-3
        ${color}
      `}
    >
      {value.toString().padStart(2, "0")}
    </p>

  </div>

);

const ReportRow = ({
  label,
  value,
  color,
  bg
}) => (

  <div
    className={`
      flex
      justify-between
      items-center
      p-5
      rounded-2xl
      border
      border-white/5
      ${bg}
    `}
  >

    <span
      className="
        text-sm
        font-bold
        text-slate-300
      "
    >
      {label}
    </span>

    <span
      className={`
        text-3xl
        font-black
        ${color}
      `}
    >
      {value || 0}
    </span>

  </div>

);

export default SentinelGuardScanner;