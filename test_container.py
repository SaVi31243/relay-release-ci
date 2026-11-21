def test_release_files(host):
    assert host.file("/opt/relay/relay.py").is_file
    assert host.file("/opt/relay/release-profile.json").is_file


def test_gunicorn_is_running(host):
    assert b"gunicorn" in host.file("/proc/1/cmdline").content


def test_port_accepts_connections(host):
    probe = (
        "import os, socket; "
        "socket.create_connection(('127.0.0.1', int(os.environ['PORT'])), 2).close()"
    )
    assert host.run("python -c %s", probe).rc == 0


def test_non_root_user(host):
    assert host.check_output("id -u") == "17061"
    assert host.check_output("grep '^Uid:' /proc/1/status").split()[1:] == ["17061"] * 4
