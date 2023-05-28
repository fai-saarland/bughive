import sys
import pynng
import flatbuffers

import msg.bughive.Response as Response
import msg.bughive.policy.Request as Request
import msg.bughive.policy.ResponseFDRTaskFD as ResponseFDRTaskFD
from msg.bughive.policy.RequestType import RequestType
from msg.bughive.Status import Status

class PolicyServer(object):
    def __init__(self):
        self.builder = flatbuffers.Builder()

    def resFDRTaskFD(self):
        task = self.fdrTaskFD()
        if task is None:
            return None

        task = self.builder.CreateString(task)

        Response.Start(self.builder)
        Response.AddStatus(self.builder, Status.OK)
        response = Response.End(self.builder)

        ResponseFDRTaskFD.Start(self.builder)
        ResponseFDRTaskFD.AddResponse(self.builder, response)
        ResponseFDRTaskFD.AddTask(self.builder, task)
        res = ResponseFDRTaskFD.End(self.builder)
        self.builder.Finish(res)
        return bytes(self.builder.Output())

    def run(self, addr):
        sock = pynng.Rep0()
        eid = sock.listen(addr)

        while True:
            data = sock.recv()
            req = Request.Request.GetRootAs(data, 0)
            reqtype = req.Request()

            response = None
            if reqtype == RequestType.REQ_FDR_TASK_FD:
                print('Got FDR_TASK_FD request')
                response = self.resFDRTaskFD()

            elif reqtype == RequestType.REQ_FDR_STATE_OPERATOR:
                print('Got FDR_STATE_OPERATOR request')
                pass

            else:
                print(f'Error: Unkown request type {reqtype}', file = sys.stderr)

            if response is not None:
                sock.send(response)

    def fdrTaskFD(self):
        raise NotImplementedError

if __name__ == '__main__':
    class Server(PolicyServer):
        def fdrTaskFD(self):
            return 'Test test test'

    s = Server()
    s.run(sys.argv[1])
