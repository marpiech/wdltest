workflow test {
    
    String testinput = "test"

    call task_one { 
        input: 
            testinput = testinput 
    }
    call task_two { 
        input: 
            testinput = testinput,
            oneinput = task_one.out
    }

    output {
        Array[File] out = task_two.out
        File? opt = task_two.opt
    }

}

task task_one {
    
    String testinput

    command {
        echo ${testinput}ONE
    }

    output {
        File out = stdout()
    }

    runtime {
        docker: "ubuntu:latest"
    }

}

task task_two {

    String testinput
    File oneinput

    command {
        mkdir out
        cat ${oneinput} > out/test1.txt
        echo ${testinput}TWO > out/test2.txt
    }

    output {
        Array[File] out = glob("out/*.txt")
        File? opt = "not available"
    }

    runtime {
        docker: "ubuntu:latest"
    }

}

