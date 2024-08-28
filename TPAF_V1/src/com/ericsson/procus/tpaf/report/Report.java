package com.ericsson.procus.tpaf.report;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutput;
import java.io.ObjectOutputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.SortedSet;
import java.util.TreeSet;

public class Report implements Serializable{

	private static final long serialVersionUID = 1L;
	private String TechPackName = "";
	private String CreationDate = "";
	private String UserName = "";
	private String TPAFVersion = "";
	private String ServerUsed = "";
	private String ServerENIQVersion = "";
	private File OutputDirectory;
	private String SupportedVendorReleases = "";
	private String BOJobType = "";
	private String ODBC = "";
	private String BISIP = "";
	private String BISUserName = "";
	private String Password = "";
	private String BIversion = "";
	private HashMap<String, ArrayList<String>> executedRules = new HashMap<String, ArrayList<String>>();
	private HashMap<String, HashMap<String, String>> AllAvailableRules = new HashMap<String, HashMap<String, String>>();
	private ArrayList<String> CreatedFiles = new ArrayList<String>();
	
	public void setTechPackName(String TechPackName){
		this.TechPackName = TechPackName;
	}
	
	public void setTPAFVersion(String TPAFVersion){
		this.TPAFVersion = TPAFVersion;
	}
	
	public void setCreatedInformation(String userName, String CreationDate){
		this.UserName = userName;
		this.CreationDate = CreationDate;
	}
	
	public void setSupportedVendorReleases(String SupportedVendorReleases){
		this.SupportedVendorReleases = SupportedVendorReleases;
	}
	
	public void setOutputDirectory(File directory){
		this.OutputDirectory = directory;
	}
	
	public void setBODetails(String jobType, String ODBC, String BISIP, String BISuser, String password, String BIversion){
		this.BOJobType = jobType;
		this.ODBC = ODBC;
		this.BISIP = BISIP;
		this.BISUserName = BISuser;
		this.Password = password;
		this.BIversion = BIversion;
	}
	
	public void setServerInformation(String ServerName, String ServerENIQVersion){
		this.ServerUsed = ServerName;
		this.ServerENIQVersion = ServerENIQVersion;
	}
	
	public void setExecutedRules(HashMap<String, ArrayList<String>> executedrules){
		this.executedRules = new HashMap<String, ArrayList<String>>(executedrules);
	}
	
	public void setAllAvailableRules(HashMap<String, HashMap<String, String>> AllAvailableRules){
		this.AllAvailableRules = AllAvailableRules;
	}
	
	public void clearCreatedfiles(){
		CreatedFiles.clear();
	}
	
	public void generateReportFile(){
		updateCreateFilesList();
		try {
			PrintWriter out = new PrintWriter(OutputDirectory.getAbsolutePath()+"\\CreationReport.txt");
			out.print("-------------------- TP AF Creation Report --------------------\n");
			out.print("TechPack Name: " + TechPackName+"\n");
			out.print("Supported Vendor Releases: " + SupportedVendorReleases+"\n");
			
			out.print("\n");
			out.print("Created by: " + UserName+"\n");
			out.print("Created date: " + CreationDate+"\n");
			out.print("TP AF version used: " + TPAFVersion+"\n");
			
			out.print("\n");
			out.print("Server used: " + ServerUsed+"\n");
			out.print("Server ENIQ version: " + ServerENIQVersion+"\n");
			
			out.print("\n");
			out.print("BO job ran: " + BOJobType+"\n");
			out.print("ODBC connection name: " + ODBC+"\n");
			out.print("BIS IP address: " + BISIP+"\n");
			out.print("BI version: " + BIversion+"\n");
			out.print("BIS user name: " + BISUserName+"\n");
			out.print("BIS password: " + Password+"\n");
			
			out.print("\n");
			out.print("\n");
			out.print("-------------------- Created Files --------------------\n");
			for(String filename : CreatedFiles){
				out.print(filename+"\n");
			}
			
			out.print("\n");
			out.print("\n");
			out.print("-------------------- Design Rules executed --------------------\n");
			
			SortedSet<String> Rulesets = new TreeSet<String>(executedRules.keySet());
			for (String Ruleset : Rulesets) {
				ArrayList<String> rules  = executedRules.get(Ruleset);
				if(rules.size()>0){
					out.print("RuleSet: "+Ruleset+"\n");
					for(String rule : rules){
						out.print("\tRule Name: "+rule+"\n");
					}
					out.print("\n");
				}
			}
			
			out.print("\n");
			out.print("\n");
			out.print("-------------------- Design Rules skipped --------------------\n");
			Rulesets = new TreeSet<String>(AllAvailableRules.keySet());
			for (String Ruleset : Rulesets) {				
				out.print("RuleSet: "+Ruleset+"\n");
				
				ArrayList<String> executedrules = new ArrayList<String>();
				if(executedRules.containsKey(Ruleset)){
					executedrules  = executedRules.get(Ruleset);
				}
				
				SortedSet<String>skippedRules = new TreeSet<String>(AllAvailableRules.get(Ruleset).keySet());
				for (String skippedRule : skippedRules) {
					if(!executedrules.contains(skippedRule)){
						out.print("\tRule Name: "+skippedRule+"\n");
					}
				}
				out.print("\n");
			}
			
			out.flush();
			out.close();

			OutputStream file = new FileOutputStream(OutputDirectory.getAbsolutePath()+"\\CreationReport.tpaf");
			OutputStream buffer = new BufferedOutputStream(file);
			ObjectOutput output = new ObjectOutputStream(buffer);
			
			output.writeObject(this);
			output.flush();
			output.close();
			
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	private void updateCreateFilesList(){
		File[] files  = OutputDirectory.listFiles();
		for(File file : files){
			if(file.isFile() && !file.getName().endsWith(".tpaf") && !file.getName().endsWith(".txt")){
				CreatedFiles.add(file.getName());
			}
			else if(file.isDirectory()){
				File[] BOfiles  = file.listFiles();
				for(File BOfile : BOfiles){
					if(BOfile.isFile() && !BOfile.getName().endsWith(".tpaf") && !BOfile.getName().endsWith(".txt")){
						CreatedFiles.add(file.getName()+"\\"+BOfile.getName());
					} 
				}
			}
		}
	}
	


}
