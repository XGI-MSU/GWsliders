#!/usr/bin/env python

"""Tests for `glue.pipeline`
"""

import tempfile
from pathlib import Path

from glue import pipeline


def _parse_submit_file(path):
    data = {}
    with open(path, "r") as file:
        for line in file:
            try:
                key, value = line.split("=", 1)
            except ValueError:
                if line.startswith("queue "):
                    key, value = line.split(maxsplit=1)
                else:
                    raise
            data[key.strip()] = value.strip()
    return data


def _parse_dag_file(path):
    dag = dict(jobs={}, maxjobs={})
    with open(path, "r") as file:
        for line in map(str.strip, file):
            if not line:  # empty
                continue
            if line.startswith("PARENT"):
                parents, _, child = line[7:].rsplit(" ", 2)
                dag["jobs"][child]["parents"] = parents.split(" ")
            else:
                key, id_, var = line.split(" ", 2)
                if key == "MAXJOBS":
                    dag["maxjobs"][id_] = int(var)
                if key == "JOB":
                    dag["jobs"][id_] = {"sub": var}
                else:
                    dag["jobs"][id_][key.lower()] = var
    return dag


class TestCondorJob:
    Job = pipeline.CondorJob

    def create(self):
        return self.Job("vanilla", "/bin/true", 1)

    def test_create(self):
        job = self.create()
        assert job.get_universe() == "vanilla"
        assert job.get_executable() == "/bin/true"

    def test_simple_sub_file(self):
        job = self.create()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            subfile = tmpdir / "test.sub"
            errfile = subfile.with_suffix(".err")
            outfile = subfile.with_suffix(".out")
            logfile = subfile.with_suffix(".log")
            job.set_sub_file(str(subfile))
            job.set_stderr_file(str(errfile))
            job.set_stdout_file(str(outfile))
            job.set_log_file(str(logfile))
            job.write_sub_file()
            sub = _parse_submit_file(subfile)
        expected = {
            "universe": "vanilla",
            "executable": "/bin/true",
            "log": str(logfile),
            "error": str(errfile),
            "output": str(outfile),
            "queue": "1",
        }
        if issubclass(self.Job, pipeline.CondorDAGJob):
            expected["notification"] = "never"
        assert sub == expected


class TestCondorDAGJob(TestCondorJob):
    Job = pipeline.CondorDAGJob
    Node = pipeline.CondorDAGNode

    def create(self):
        return self.Job("vanilla", "/bin/true")

    def test_create(self):
        job = self.create()
        assert job.get_universe() == "vanilla"
        assert job._CondorJob__notification == "never"

    def test_create_node(self):
        job = self.create()
        assert isinstance(job.create_node(), self.Node)


class TestCondorDAG:
    Dag = pipeline.CondorDAG
    Job = pipeline.CondorDAGJob
    Node = pipeline.CondorDAGNode

    def job(self, jobdir, universe, executable):
        jobdir = Path(jobdir)
        job = self.Job(universe, executable)
        subfile = jobdir / "test.sub"
        job.set_sub_file(str(subfile))
        job.set_stderr_file(str(subfile.with_suffix(".err")))
        job.set_stdout_file(str(subfile.with_suffix(".out")))
        job.set_log_file(str(subfile.with_suffix(".log")))
        return job

    def test_create(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # create a DAG
            dag = self.Dag(str(tmpdir / "test.log"))
            dag.set_dag_file(str(tmpdir / "test"))

            # add a job
            job1 = self.job(tmpdir, "vanilla", "/bin/true")
            parents = []
            for i in range(5):
                node = self.Node(job1)
                node.set_category("a")
                node.set_retry(1)
                dag.add_node(node)
                parents.append(node)

            job2 = self.job(tmpdir, "vanilla", "/bin/false")
            for i in range(5):
                node = self.Node(job2)
                node.set_category("b")
                node.set_retry(1)
                for par in parents:
                    node.add_parent(par)
                dag.add_node(node)

            # write all the files
            dag.write_sub_files()
            dag.write_dag()
            dag.write_script()

            # read back the DAG file
            dag = _parse_dag_file(dag.get_dag_file())

        assert len(dag["jobs"]) == 10
        assert dag["maxjobs"] == {}
        # check that the complete list of sub files referenced in the DAG
        # matches the sub files for the jobs we created
        assert {
            x["sub"] for x in dag["jobs"].values()
        } == {job1.get_sub_file(), job2.get_sub_file()}
