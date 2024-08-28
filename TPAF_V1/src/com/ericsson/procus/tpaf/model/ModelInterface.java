package com.ericsson.procus.tpaf.model;

import java.util.ArrayList;
import java.util.HashMap;

import com.ericsson.procus.tpaf.utils.ModelException;

public interface ModelInterface{

	public void populateModelFromFDdictionary() throws ModelException;
	public void loadDictionaryFromFD(String filepath) throws ModelException;
	public void populateModelFromTPIdictionary() throws ModelException;
	public void loadDictionaryFromTpi(String filepath) throws ModelException;
	public void populateModelFromXML(String filepath) throws ModelException;
	public void populateModelFromServer(String serverName, String TPName) throws ModelException;
	
	public ArrayList<String> getTPNameFromServer(String serverName);
	
	public int runDifference(ModelInterface diffModel, String outputDir) throws ModelException;
	public String DecryptTpi(String filepath) throws ModelException;
	
	public String getTechPackName();
	public String getProductNumber();
	public String getEniqVersion();
	public String getRstate();
	public String getLoadSource();
	public void setLoadSource(String location);
	public String getLoadDate();
	public void setLoadDate(String date);
	public String getModelUID();
	public HashMap<String, String> getVersioningInformation();
	public String getTechPackOutputName();
	public String getSupportedVendorReleases();
	public String getServerENIQVersion(String server);
	public void updateLockedInfo(String LockedBy, String LockedDate);
	public void updateENIQversion(String ENIQversion);
	
	public void setupENIQEnvironment(String server, String path) throws ModelException;
	
	public void createTechPack(String server) throws ModelException;
	public void createTechPackSets(String server, String outputPath) throws ModelException;
	public void activateTechPack(String server) throws ModelException;
	public void createTechPacktpi(String server, int build, String outputPath, String encrypt) throws ModelException;
	
	public void deactivateTechPack(String server) throws ModelException;
	public void deleteSetsTechPack(String server) throws ModelException;
	public void deleteTechPack(String server) throws ModelException;
	
	public void createInterfaces(String server) throws ModelException;
	public void createInterfaceSets(String server, String outputPath) throws ModelException;
	public void createInterfacetpis(String server, String outputPath, String encrypt) throws ModelException;
	public void activateInterfaces(String server) throws ModelException;
	
	public void deActivateInterfaces(String server) throws ModelException;
	public void deleteInterfaces(String server) throws ModelException;
	
	public void createTechPackDescDoc(String server, String outputPath) throws ModelException;
	public void createTechPackXLSDoc(String templateLocation, String outputPath) throws ModelException;
	public void createTechPackXMlDoc(String outputPath) throws ModelException;
	
	public void initBOUniverse(String outputDir, String BIversion) throws ModelException;
	public void createUniverse(String BISIP, String ODBC, String repDb, String username, String password) throws ModelException;
	public void updateUniverse(String BISIP, String ODBC, String repDb, String username, String password) throws ModelException;
	public void createVerificationReports(String BISIP, String ODBC, String repDb, String username, String password) throws ModelException;
	public void createBOReferenceDoc(String BISIP, String ODBC, String repDb, String username, String password) throws ModelException;
	public void createBOPackage(String LockedBy, String encrypt) throws ModelException;
	
	public HashMap<String, HashMap<String, String>> getRuleSetProperties(String RuleSetPath)throws ModelException;
	public HashMap<String, HashMap<String, ArrayList<String>>> executeRules(String moduleName, ArrayList<String> rulestoRun)throws ModelException;
	
}
