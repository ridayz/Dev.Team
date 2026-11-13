// Native Windows launcher for a local dashboard.
//
// Double-click the compiled .exe: if the server is not running it starts it
// hidden, waits until the port answers, then opens the default browser and
// parks a tray icon so the same window can be reopened or the server stopped.
//
// Built twice from this one file with /define:RADAR or /define:DARKFIBER.
using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Forms;

static class Program
{
#if RADAR
    const string AppTitle = "Free Model Radar";
    const string MutexName = "Local\\FreeModelRadar.Launcher";
    const string RuntimeName = "node";
    const string ServerArgs = "server.mjs";
    const int Port = 4173;
#elif DARKFIBER
    const string AppTitle = "Dark Fiber Core Manager";
    const string MutexName = "Local\\DarkFiberManager.Launcher";
    const string RuntimeName = "pythonw";
    const string ServerArgs = "src\\server\\app.py";
    const int Port = 4174;
#else
#error Compile with /define:RADAR or /define:DARKFIBER
#endif

    static readonly string BaseUrl = "http://127.0.0.1:" + Port + "/";
    static Process child;
    static bool ownsServer;
    static string logPath;

    [STAThread]
    static void Main()
    {
        bool isFirst;
        Mutex mutex = new Mutex(true, MutexName, out isFirst);
        if (!isFirst)
        {
            // Already running: just bring the dashboard back.
            OpenBrowser();
            return;
        }

        try
        {
            logPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "Dev.Team", "logs");
            Directory.CreateDirectory(logPath);
            logPath = Path.Combine(logPath, ("server-" + Port) + ".log");

            if (!PortOpen())
            {
                if (!StartServer())
                {
                    MessageBox.Show(
                        "Server tidak bisa dijalankan." + Environment.NewLine + Environment.NewLine +
                        "Log: " + logPath,
                        AppTitle, MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }
                ownsServer = true;
                if (!WaitForPort(45))
                {
                    MessageBox.Show(
                        "Server belum merespons di " + BaseUrl + " setelah 45 detik." + Environment.NewLine +
                        "Log: " + logPath,
                        AppTitle, MessageBoxButtons.OK, MessageBoxIcon.Warning);
                }
            }

            OpenBrowser();
            Application.EnableVisualStyles();
            Application.Run(new TrayContext(mutex));
        }
        catch (Exception ex)
        {
            MessageBox.Show(AppTitle + " gagal dijalankan: " + ex.Message,
                AppTitle, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    sealed class TrayContext : ApplicationContext
    {
        readonly NotifyIcon tray;
        readonly ToolStripMenuItem statusItem;
        readonly Mutex mutex;

        public TrayContext(Mutex m)
        {
            mutex = m;

            statusItem = new ToolStripMenuItem(StatusText());
            statusItem.Enabled = false;

            ToolStripMenuItem open = new ToolStripMenuItem("Buka dashboard");
            open.Font = new Font(open.Font, FontStyle.Bold);
            open.Click += delegate { OpenBrowser(); };

            ToolStripMenuItem copy = new ToolStripMenuItem("Salin alamat " + BaseUrl.TrimEnd('/'));
            copy.Click += delegate { try { Clipboard.SetText(BaseUrl); } catch { } };

            ToolStripMenuItem stop = new ToolStripMenuItem("Hentikan server & keluar");
            stop.Click += delegate { StopServer(); ExitThread(); };

            ToolStripMenuItem quit = new ToolStripMenuItem("Tutup ikon (server tetap jalan)");
            quit.Click += delegate { ExitThread(); };

            ContextMenuStrip menu = new ContextMenuStrip();
            menu.Items.Add(statusItem);
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add(open);
            menu.Items.Add(copy);
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add(stop);
            menu.Items.Add(quit);

            tray = new NotifyIcon();
            tray.Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            tray.Text = AppTitle;
            tray.ContextMenuStrip = menu;
            tray.Visible = true;
            tray.DoubleClick += delegate { OpenBrowser(); };
            tray.BalloonTipTitle = AppTitle;
            tray.BalloonTipText = "Aktif di " + BaseUrl + " — klik dua kali untuk membuka.";
            tray.ShowBalloonTip(4000);

            if (child != null)
            {
                child.EnableRaisingEvents = true;
                child.Exited += delegate { statusItem.Text = AppTitle + ": server berhenti"; };
            }
        }

        string StatusText()
        {
            return ownsServer
                ? AppTitle + " — jalan di port " + Port
                : AppTitle + " — port " + Port + " sudah dipakai proses lain";
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && tray != null)
            {
                tray.Visible = false;
                tray.Dispose();
            }
            base.Dispose(disposing);
        }

        protected override void ExitThreadCore()
        {
            base.ExitThreadCore();
            if (mutex != null) mutex.ReleaseMutex();
        }
    }

    // ---------- server process ----------

    static bool StartServer()
    {
        string exe = ResolveRuntime();
        if (exe == null)
        {
            MessageBox.Show(
                "Runtime tidak ditemukan (" + RuntimeName + ")." + Environment.NewLine +
                "Pasang dulu, lalu jalankan lagi.",
                AppTitle, MessageBoxButtons.OK, MessageBoxIcon.Error);
            return false;
        }

        ProcessStartInfo psi = new ProcessStartInfo(exe, ServerArgs);
        psi.WorkingDirectory = AppDomain.CurrentDomain.BaseDirectory;
        psi.UseShellExecute = false;
        psi.CreateNoWindow = true;
        psi.RedirectStandardOutput = true;
        psi.RedirectStandardError = true;
        psi.EnvironmentVariables["PORT"] = Port.ToString();
        psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
        psi.EnvironmentVariables["PYTHONUTF8"] = "1";
        psi.EnvironmentVariables["PYTHONUNBUFFERED"] = "1";

        try
        {
            child = new Process();
            child.StartInfo = psi;
            child.OutputDataReceived += delegate(object s, DataReceivedEventArgs e) { Log(e.Data); };
            child.ErrorDataReceived += delegate(object s, DataReceivedEventArgs e) { Log(e.Data); };
            child.Start();
            child.BeginOutputReadLine();
            child.BeginErrorReadLine();
            Log("--- start " + exe + " " + ServerArgs + " (port " + Port + ") ---");
            return true;
        }
        catch (Exception ex)
        {
            Log("gagal start: " + ex.Message);
            return false;
        }
    }

    static string ResolveRuntime()
    {
        // Runtime yang sudah pasti ada di mesin ini lebih diprioritaskan.
#if DARKFIBER
        string[] known =
        {
            @"D:\tools\python312\pythonw.exe",
            @"D:\tools\python312\python.exe",
        };
#else
        string[] known =
        {
            @"C:\Program Files\nodejs\node.exe",
            @"C:\Program Files (x86)\nodejs\node.exe",
        };
#endif
        foreach (string path in known)
            if (File.Exists(path)) return path;

        string[] dirs = (Environment.GetEnvironmentVariable("PATH") ?? "").Split(';');
        foreach (string dir in dirs)
        {
            if (dir.Trim().Length == 0) continue;
            string candidate = Path.Combine(dir.Trim(), RuntimeName + ".exe");
            if (File.Exists(candidate)) return candidate;
        }
        return null;
    }

    static bool PortOpen()
    {
        try
        {
            using (TcpClient client = new TcpClient())
            {
                IAsyncResult ar = client.BeginConnect("127.0.0.1", Port, null, null);
                if (!ar.AsyncWaitHandle.WaitOne(400)) return false;
                client.EndConnect(ar);
                return true;
            }
        }
        catch
        {
            return false;
        }
    }

    static bool WaitForPort(int seconds)
    {
        for (int i = 0; i < seconds * 4; i++)
        {
            if (PortOpen()) return true;
            Thread.Sleep(250);
        }
        return PortOpen();
    }

    static void StopServer()
    {
        try
        {
            if (child != null && !child.HasExited)
            {
                child.Kill();
                child.WaitForExit(4000);
            }
        }
        catch { }

        int pid = PortOwnerPid();
        if (pid > 0)
        {
            try { Process.GetProcessById(pid).Kill(); } catch { }
        }
    }

    static int PortOwnerPid()
    {
        try
        {
            ProcessStartInfo psi = new ProcessStartInfo("netstat", "-ano -p TCP");
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            using (Process p = Process.Start(psi))
            {
                string output = p.StandardOutput.ReadToEnd();
                p.WaitForExit(4000);
                string needle = ":" + Port + " ";
                foreach (string raw in output.Split('\n'))
                {
                    string line = raw.Trim();
                    if (!line.Contains(needle)) continue;
                    if (!line.Contains("LISTENING")) continue;
                    string[] parts = line.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                    int pid;
                    if (int.TryParse(parts[parts.Length - 1], out pid)) return pid;
                }
            }
        }
        catch { }
        return 0;
    }

    static void OpenBrowser()
    {
        try
        {
            Process.Start(new ProcessStartInfo(BaseUrl) { UseShellExecute = true });
        }
        catch (Exception ex)
        {
            Log("gagal buka browser: " + ex.Message);
        }
    }

    static readonly object logLock = new object();

    static void Log(string line)
    {
        if (line == null || logPath == null) return;
        try
        {
            lock (logLock)
            {
                File.AppendAllText(logPath, line + Environment.NewLine, Encoding.UTF8);
            }
        }
        catch { }
    }
}
