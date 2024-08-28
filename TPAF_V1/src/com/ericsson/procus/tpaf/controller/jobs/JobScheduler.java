package com.ericsson.procus.tpaf.controller.jobs;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class JobScheduler {
	private ScheduledExecutorService SERVICE = Executors.newSingleThreadScheduledExecutor();
	private static JobScheduler js;
	private static int instance;
	
	public void scheduleJob(JobBase job){
		SERVICE.schedule(job, 1, TimeUnit.SECONDS);
		try{
			job.scheduled();
		}catch(Exception e){
			System.out.println("Initial draw attempt failed");
		}
	}
	
	public void shutdown(){
		SERVICE.shutdownNow();
	}
	
	
	private JobScheduler(){
		js = this;
	}
	
	public static JobScheduler getInstance(){
		if(instance ==0){
			instance = 1;
			return new JobScheduler();
		}
		if(instance == 1){
			return js;
		}
		
		return null;
	}
	
}
