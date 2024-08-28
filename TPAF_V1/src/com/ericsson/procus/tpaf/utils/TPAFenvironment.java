package com.ericsson.procus.tpaf.utils;

public class TPAFenvironment {
	//Product properties
	public static final String USERNAME = System.getProperty("user.name");
	public static final String PRODUCTRSTATE = System.getProperty("ProdcutRstate", "R2L");
	public static final String PRODUCTNAME = System.getProperty("ProductName", "TP AF");
	public static final String[] OPTIONS = {"Design","Universe","Analysis","Test","CPI","Packaging"};
	
	//Directory locations
	public static final String ENVBASEDIR = System.getProperty("user.home")+"\\TPAF";
	public static final String CSSDIR = ENVBASEDIR+"\\css";
	public static final String ENVDIR = ENVBASEDIR+"\\Environment";
	public static final String OUTPUTDIR = ENVBASEDIR+"\\Output";
	
	//CSS Properties
	public static final String CSSFILENAME = System.getProperty("CssFile", "Styling.css");
		//BACKGROUNDS
	public static final String BASE_BACKGROUND = System.getProperty("BaseBackground", "BaseBackground");
	public static final String TITLEBAR_BACKGROUND = System.getProperty("TitleBarBackground", "titleBarBackground");
	public static final String LIST_BACKGROUND = System.getProperty("ListBackground", "listBackground");
		//FONT SIZES
	public static final String SMALLFONT = System.getProperty("smallfont", "smallfont");
	public static final String MEDIUMFONT = System.getProperty("mediumfont", "mediumfont");
	public static final String LARGEFONT = System.getProperty("largefont", "largefont");
	public static final String XLFONT = System.getProperty("Xlfont", "Xlfont");
		//FONT COLOURS
	public static final String WHITEFONT = System.getProperty("WhiteFont", "fontWhite");
	public static final String BLACKFONT = System.getProperty("BlackFont", "fontBlack");
	public static final String GREENFONT = System.getProperty("GreenFont", "fontGreen");
	public static final String REDFONT = System.getProperty("RedFont", "fontRed");
	public static final String BLUEFONT = System.getProperty("BlueFont", "fontBlue");
		//INPUT BUTTONS
	public static final String FDLOAD = System.getProperty("FDLoad", "FDLoad");
	public static final String SERVERLOAD = System.getProperty("serverLoad", "serverLoad");
	public static final String TPILOAD = System.getProperty("tpiLoad", "tpiLoad");
	public static final String XMLLOAD = System.getProperty("xmlLoad", "xmlLoad");
	public static final String BUTTONSTYLE = System.getProperty("buttonStyle", "buttonStyle");
}
