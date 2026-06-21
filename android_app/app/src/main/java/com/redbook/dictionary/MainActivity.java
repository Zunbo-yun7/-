package com.redbook.dictionary;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends AppCompatActivity {

    private static final int CHECK_INTERVAL_MS = 500;
    private static final int MAX_WAIT_TIME_MS = 30000;
    private static final String LOCAL_URL = "http://127.0.0.1:5000";

    private ProgressBar progressBar;
    private TextView statusText;
    private int waitedMs = 0;

    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        progressBar = findViewById(R.id.progressBar);
        statusText = findViewById(R.id.statusText);

        statusText.setText("正在启动词典服务...");
        progressBar.setVisibility(View.VISIBLE);

        // 在后台线程检查服务器是否就绪
        new Thread(this::waitForServer).start();
    }

    private void waitForServer() {
        while (waitedMs < MAX_WAIT_TIME_MS) {
            if (isServerReady()) {
                runOnUiThread(this::launchServerActivity);
                return;
            }
            waitedMs += CHECK_INTERVAL_MS;
            try {
                Thread.sleep(CHECK_INTERVAL_MS);
            } catch (InterruptedException e) {
                break;
            }
        }
        runOnUiThread(this::showServerError);
    }

    private boolean isServerReady() {
        HttpURLConnection conn = null;
        try {
            URL url = new URL(LOCAL_URL);
            conn = (HttpURLConnection) url.openConnection();
            conn.setConnectTimeout(1000);
            conn.setReadTimeout(1000);
            conn.setRequestMethod("GET");
            int code = conn.getResponseCode();
            return code == 200;
        } catch (IOException e) {
            return false;
        } finally {
            if (conn != null) {
                conn.disconnect();
            }
        }
    }

    private void launchServerActivity() {
        progressBar.setVisibility(View.GONE);
        Intent intent = new Intent(this, LocalServerActivity.class);
        startActivity(intent);
        finish();
    }

    private void showServerError() {
        progressBar.setVisibility(View.GONE);
        statusText.setText("无法启动服务，请确保已安装并运行红宝书词典桌面版！");
        statusText.setTextSize(16);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        mainHandler.removeCallbacksAndMessages(null);
    }
}
