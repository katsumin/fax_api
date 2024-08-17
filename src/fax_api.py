from flask import Flask, request, send_file
from flask_restx import Resource, Api, reqparse
import werkzeug
import subprocess
import re
from flask_cors import CORS
import os
import socket

app = Flask(__name__)
api = Api(app)

send_req = reqparse.RequestParser()
send_req.add_argument(
    'tel_no', type=str, location='form', help='送信先電話番号')
send_req.add_argument(
    'send_file', type=werkzeug.datastructures.FileStorage, location='files', help='送信ファイル')


class FaxBase(Resource):
    def exec_proc(self, cmdlines: list[str]) -> list[str]:
        """
        コマンド実行

        Parameters
        ----------
        cmdlines: list[str]
            コマンドライン文字列
        """
        proc = subprocess.Popen(cmdlines, stdout=subprocess.PIPE)
        l = []
        for line in proc.stdout:
            try:
                l.append(line.decode("utf-8"))
            except Exception as err:
                print(err)
            finally:
                pass
        return l


@api.route("/fax/send")
class FaxSend(FaxBase):
    def get(self):
        """
        FAX送信状態取得
        """
        status = []
        lines = self.exec_proc(["sudo", "faxstat", "-s"])
        for f in lines:
            status.append(f.strip("\r\n"))
        return {'status': status}

    @api.expect(send_req)
    def post(self):
        """
        FAX送信

        Parameters
        ----------
        tel_no: string
            送信先電話番号
        send_file: file
            送信ファイル
        """
        tel_no = request.form['tel_no']
        send_file = request.files['send_file']
        if tel_no == "" or send_file == "":
            return {'message': "argument error"}, 400
        send_filename = f"./{send_file.filename}"
        print(send_filename)
        send_file.save(send_filename)
        lines = self.exec_proc(
            ["sudo", "sendfax", "-n", "-d", tel_no, send_filename])
        print(lines)
        for l in lines:
            if l.startswith("request id is"):
                m = re.search(r'\d+', l)
                job_id = m.group()
                return {'tel_no': tel_no, 'send_file': send_filename, 'job_id': job_id}
        return {'messages': lines}, 500


@api.route("/fax/send/<string:job_id>")
class FaxSend(FaxBase):
    def delete(self, job_id):
        """
        FAX送信待ちジョブの削除

        Parameters
        ----------
        job_id: string
            FAX送信待ちジョブID
        """
        # print(job_id)
        msg = "other error"
        try:
            lines = self.exec_proc(["sudo", "faxrm",  job_id])
            print(lines)
            return {}
        except OSError as err:
            print(f'OSError: {err.strerror}')
            msg = err.strerror
        except Exception as err:
            print(f'Exception: {err}')
        return {'messages': msg}, 500


@ api.route("/fax/receives")
class FaxReceives(FaxBase):
    def get(self):
        """
        FAX受信状態取得
        """
        user = os.getenv("USER")
        list = []
        lines = self.exec_proc(["sudo", "-u", user, "faxstat", "-r"])
        for f in lines:
            f = f.strip("\r\n")
            if f.endswith(".tif"):
                #     cols = f.split(" ")
                #     list.append({
                #         "date": cols[len(cols)-2],
                #         "file": cols[len(cols)-1]})
                cols = f.split(",")
                list.append({
                    "date": cols[0],
                    "pages": cols[1],
                    "sender": cols[2],
                    "time": cols[3],
                    "file": cols[4],
                })
        return {'receives': list}


@api.route("/fax/receive/<string:recv_file>")
class FaxReceive(FaxBase):
    def get(self, recv_file):
        """
        FAX受信ファイル取得

        Parameters
        ----------
        recv_file: string
            受信ファイル名
        """
        ms = 'other error'
        try:
            f = f'/var/spool/hylafax/recvq/{recv_file}'
            return send_file(f, as_attachment=True, mimetype="image/tiff")
        except OSError as err:
            msg = err.strerror
        finally:
            pass
        return {'message': msg}, 500


if __name__ == '__main__':
    connect_interface = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connect_interface.connect(("8.8.8.8", 80))
    host = connect_interface.getsockname()[0]
    cors = CORS(app, resources={
                r"/*": {"origins": f'http://{host}:3000'}})
    app.run(debug=True, host='0.0.0.0')
