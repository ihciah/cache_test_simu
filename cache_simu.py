# -*- coding: utf-8 -*-
#__author__='ihciah'
#__stu_NO__='13307130364'
import sys,getopt,math,time

class CacheSimu:
    trace_file=''
    cache_size=''
    associativity=''
    block_size=''
    trace=[]
    hits=0
    lrulist=[]
    def __init__(self):
        opts, args = getopt.getopt(sys.argv[1:], "t:a:s:b:")
        for op, value in opts:
            if op=='-t':
                self.trace_file=value
                f=open(value,'r')
                self.trace=f.readlines()
            elif op=='-s':
                self.cache_size=value
                if value[-1:]=='k' or value[-1:]=='K':
                    self.cache_size=long(value[:-1])*1024
                else:
                    self.cache_size=long(self.cache_size)
                if self.cache_size<1024 or self.cache_size>(64*1024):
                    self.usage('cache_size %s is not valid(1K to 64K).\nTIP:tpye 1024 is equal to type 1K' %value)
            elif op=='-a':
                self.associativity=int(value)
            elif op=='-b':
                self.block_size=int(value)
                if self.block_size not in [32,64,128,256]:
                    self.usage('block_size %s is not valid.' %value)
                self.log_blocksize=int(math.log(self.block_size,2))
            else:
                self.usage('Invalid option %s' %op)
        if self.trace_file=='' or self.cache_size=='' or self.associativity=='' or self.block_size=='':
            self.usage()
        self.maxline=self.cache_size/self.block_size
    def usage(self,addi=''):
        print 'Usage:%s -t tracefile -s cachesize -b blocksize -a associativity\nIf fully-associative please set associativity to 0.\n%s' %(sys.argv[0],addi)
        sys.exit()
    def output_statics(self):
        total=len(self.trace)
        print 'program_name: go_ld_trace'
        print 'cache_size: %dKB' %(self.cache_size/1024)
        print 'block_size: %d' %self.block_size
        print 'associativity: %d' %self.associativity
        print 'total_lds: %d' %total
        print 'cache_hits: %d' %self.hits
        print 'cache_misses: %d' %(total-self.hits)
        print 'cache_miss_rate: %.2f' %(float(total-self.hits)/total)
        print 'time_spent: %.2f sec' %self.tictoc
    def alllru(self,x):
        if x in self.lrulist:
            self.hits+=1
            self.lrulist.remove(x)
        elif len(self.lrulist)>=self.maxline:
            del self.lrulist[0]
        self.lrulist.append(x)

    def grouplru(self,x):
        group_of_x=x%self.groups
        if x in self.lrulist[group_of_x]:
            self.hits+=1
            self.lrulist[group_of_x].remove(x)
        elif len(self.lrulist[group_of_x])>=self.associativity:
            del self.lrulist[group_of_x][0]
        self.lrulist[group_of_x].append(x)

    def calc(self):
        current=0
        tic=time.clock()
        if self.associativity>0:
            #组相联映射
            self.groups=self.maxline/self.associativity#组数，每组self.associativity个
            self.lrulist=[[] for _ in range(self.groups)]
            for line in self.trace:
                current+=long(line.replace('\n','').replace('\r','').replace(' ',''))
                self.grouplru(current>>self.log_blocksize)
        else:
            #全相联映射
            for line in self.trace:
                current+=long(line.replace('\n','').replace('\r','').replace(' ',''))
                self.alllru(current>>self.log_blocksize)
        toc=time.clock()
        self.tictoc=toc-tic
        self.output_statics()

if __name__ == '__main__':
    c=CacheSimu()
    c.calc()
