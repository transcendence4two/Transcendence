package br.com.transcendence.friends.infrastructure.logging;

import org.jboss.logmanager.ExtLogRecord;

import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogRecord;

public class LogstashTcpHandler extends Handler {

    private static final DateTimeFormatter ISO_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'").withZone(ZoneOffset.UTC);

    private final String host;
    private final int port;
    private final String serviceName;
    private final String serviceEnvironment;

    private Socket socket;
    private PrintWriter writer;

    public LogstashTcpHandler(String host, int port, String serviceName, String serviceEnvironment) {
        this.host = host;
        this.port = port;
        this.serviceName = serviceName;
        this.serviceEnvironment = serviceEnvironment;
        connect();
    }

    private synchronized void connect() {
        try {
            socket = new Socket(host, port);
            writer = new PrintWriter(
                    new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8), true);
        } catch (IOException e) {
            socket = null;
            writer = null;
        }
    }

    @Override
    public synchronized void publish(LogRecord record) {
        if (!isLoggable(record)) return;
        try {
            if (writer == null) connect();
            if (writer == null) return;
            writer.println(buildJson(record));
            if (writer.checkError()) {
                close();
            }
        } catch (Exception e) {
            close();
        }
    }

    private String buildJson(LogRecord record) {
        StringBuilder sb = new StringBuilder(512);
        String timestamp = ISO_FORMATTER.format(Instant.ofEpochMilli(record.getMillis()));

        sb.append("{");
        appendField(sb, "@timestamp", timestamp);
        sb.append(",");
        appendField(sb, "log.level", mapLevel(record.getLevel()));
        sb.append(",");
        appendField(sb, "message", record.getMessage() != null ? record.getMessage() : "");
        sb.append(",");
        appendField(sb, "service.name", serviceName);
        sb.append(",");
        appendField(sb, "service.environment", serviceEnvironment);
        sb.append(",");
        appendField(sb, "logger.name", record.getLoggerName() != null ? record.getLoggerName() : "");

        if (record instanceof ExtLogRecord ext) {
            Map<String, String> mdc = ext.getMdcCopy();
            if (mdc != null) {
                for (Map.Entry<String, String> entry : mdc.entrySet()) {
                    if (entry.getValue() != null) {
                        sb.append(",");
                        appendField(sb, entry.getKey(), entry.getValue());
                    }
                }
            }
        }

        sb.append("}");
        return sb.toString();
    }

    private String mapLevel(Level level) {
        if (level == null) return "info";
        int v = level.intValue();
        if (v >= Level.SEVERE.intValue()) return "error";
        if (v >= Level.WARNING.intValue()) return "warning";
        return "info";
    }

    private void appendField(StringBuilder sb, String key, String value) {
        sb.append("\"").append(escape(key)).append("\":\"").append(escape(value)).append("\"");
    }

    private String escape(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    @Override
    public void flush() {
    }

    @Override
    public synchronized void close() {
        try {
            if (socket != null) socket.close();
        } catch (IOException ignored) {
        }
        socket = null;
        writer = null;
    }
}
