all:../libbam.a ../samtools ex1.glf ex1.pileup.gz ex1.bam.bai ex1.glfview.gz calDepth
		@echo; echo \# You can now launch the viewer with: \'samtools tview ex1.bam ex1.fa\'; echo;

ex1.fa.fai:ex1.fa
		../samtools faidx ex1.fa
ex1.bam:ex1.sam.gz ex1.fa.fai
		../samtools import ex1.fa.fai ex1.sam.gz ex1.bam
ex1.bam.bai:ex1.bam
		../samtools index ex1.bam
ex1.pileup.gz:ex1.bam ex1.fa
		../samtools pileup -cf ex1.fa ex1.bam | gzip > ex1.pileup.gz
ex1.glf:ex1.bam ex1.fa
		../samtools pileup -gf ex1.fa ex1.bam > ex1.glf
ex1.glfview.gz:ex1.glf
		../samtools glfview ex1.glf | gzip > ex1.glfview.gz

../samtools:
		(cd ..; make samtools)

../libbam.a:
		(cd ..; make libbam.a)

calDepth:../libbam.a calDepth.c
		gcc -g -Wall -O2 -I.. calDepth.c -o $@ -lm -lz -L.. -lbam

clean:
		rm -fr *.bam *.bai *.glf* *.fai *.pileup* *~ calDepth *.dSYM