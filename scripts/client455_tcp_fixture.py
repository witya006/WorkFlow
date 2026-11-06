"""A bounded TCP acceptance fixture for OWN client probes;no RF protocol responses."""
import socket,threading

class TcpAcceptanceFixture:
    def __init__(self,enabled=True):
        self.enabled=enabled;self.port=1;self.accepted=0;self.received=0;self.failure=None;self.finished=threading.Event();self.thread=None
    def __enter__(self):
        if self.enabled:
            self.listener=socket.socket();self.listener.bind(('127.0.0.1',0));self.port=self.listener.getsockname()[1];self.listener.listen(1);self.listener.settimeout(.2)
            self.thread=threading.Thread(target=self._run,daemon=True);self.thread.start()
        return self
    def _run(self):
        peer=None
        try:
            while not self.finished.is_set() and peer is None:
                try:peer,_=self.listener.accept();self.accepted+=1;peer.settimeout(.2)
                except socket.timeout:pass
            while peer is not None and not self.finished.is_set():
                try:
                    data=peer.recv(4096)
                    if not data:break
                    self.received+=len(data)
                except socket.timeout:pass
        except ConnectionResetError:
            pass # An own debugger/probe may terminate its client at a checkpoint.
        except OSError as error:
            if not self.finished.is_set():self.failure=repr(error)
        finally:
            if peer is not None:peer.close()
    def __exit__(self,*unused):
        self.finished.set()
        if self.enabled:
            self.listener.close();self.thread.join(3)
            if self.thread.is_alive():raise RuntimeError('Own TCP fixture has not stopped')
            if self.failure:raise RuntimeError(self.failure)
    def report(self):
        return {'enabled':self.enabled,'loopback_port':self.port,'accepted_connections':self.accepted,'bytes_received':self.received,'bytes_sent':0,'rf_protocol_responses':False,'authentication_performed':False,'thread_stopped':self.thread is None or not self.thread.is_alive()}
