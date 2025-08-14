import json, requests, urllib3

class SplunkHEC:
    def __init__(self, base_url, token, verify=True, default_index=None, default_sourcetype=None, timeout=30):
        """
        base_url: e.g. https://localhost:8088
        token: HEC token string
        verify: True, False, or path to CA bundle
        """
        self.url = base_url.rstrip("/") + "/services/collector"
        self.verify = verify
        self.timeout = timeout
        self.default_index = default_index
        self.default_sourcetype = default_sourcetype
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Splunk {token}"})
        if verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def send(self, events, index=None, sourcetype=None, host=None, epoch_time=None, batch_size=500):
        """events: iterable of dicts (each becomes event=<dict>)"""
        buf = []
        def wrap(e):
            payload = {"event": e}
            if index or self.default_index: payload["index"] = index or self.default_index
            if sourcetype or self.default_sourcetype: payload["sourcetype"] = sourcetype or self.default_sourcetype
            if host: payload["host"] = host
            if epoch_time is not None: payload["time"] = epoch_time
            return json.dumps(payload)

        for e in events:
            buf.append(wrap(e))
            if len(buf) >= batch_size:
                self._post("\n".join(buf)); buf.clear()
        if buf:
            self._post("\n".join(buf))

    def send_one(self, event, **kw):
        self.send([event], **kw)

    def _post(self, payload_str):
        r = self.session.post(self.url, data=payload_str, verify=self.verify, timeout=self.timeout)
        if r.status_code != 200:
            raise RuntimeError(f"HEC {r.status_code}: {r.text}")
        return r.json()
