package com.ericsson.procus.tpaf.encryption;

//import com.ericsson.eniq.licensing.cache.*;
import java.io.*;
import java.net.MalformedURLException;
import java.rmi.*;
import java.util.Enumeration;
import java.util.Properties;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import org.apache.tools.ant.BuildException;

// Referenced classes of package com.distocraft.dc5000.install.ant:
//            ZipCrypter

public class ZipCrypterExtractor extends ZipCrypter
{

    public ZipCrypterExtractor()
    {
        outputDir = null;
    }

    public void execute()
        throws BuildException
    {
        initKey();
        if(fileTarget == null)
            throw new BuildException("The target file has not been specified.");
        File inputFiles[] = {
            new File("")
        };
        if(fileTarget.isFile())
            inputFiles[0] = fileTarget;
        else
            inputFiles = fileTarget.listFiles();
label0:
        for(int i = 0; i < inputFiles.length; i++)
        {
            File destDir = getDestinationDir(inputFiles[i]);
            if(destDir == null)
                continue;
            System.out.println((new StringBuilder()).append("Extracting ").append(inputFiles[i].getName()).toString());
            try
            {
                ZipFile zf = new ZipFile(inputFiles[i]);
//                if(!isLicenseValid(zf))
//                {
//                    System.out.println((new StringBuilder()).append("Not extracting ").append(inputFiles[i].getName()).append(" because license is not valid!").toString());
//                    continue;
//                }
                System.out.println((new StringBuilder()).append("Extracting ").append(inputFiles[i].getName()).append(". License is valid!").toString());
                Enumeration entries = zf.entries();
                do
                {
                    if(!entries.hasMoreElements())
                        continue label0;
                    ZipEntry ze = (ZipEntry)entries.nextElement();
                    if(ze.isDirectory())
                    {
                        File dir = new File(outputDir, ze.getName());
                        dir.mkdir();
                    } else
                    {
                        long startTime = System.currentTimeMillis();
                        System.out.println((new StringBuilder()).append("Processing .zip entry: ").append(ze.getName()).toString());
                        //ZipCrypter.ZipCrypterDataEntry output = cryptInputStream(zf.getInputStream(ze), cryptMode, ze.getExtra(), rsaKey);
                        File outFile = new File(destDir, ze.getName());
                        outFile.getParentFile().mkdirs();
                        FileOutputStream fos = new FileOutputStream(outFile);
                        //fos.write(output.getData());
                        fos.close();
                        double totalTime = (double)(System.currentTimeMillis() - startTime) / 1000D;
                        System.out.println((new StringBuilder()).append("Processed ").append(ze.getSize()).append(" bytes in ").append(totalTime).append(" seconds.").toString());
                    }
                } while(true);
            }
            catch(Exception e)
            {
                throw new BuildException(e.getMessage(), e);
            }
        }

    }

//    private boolean isLicenseValid(ZipFile zf)
//        throws BuildException
//    {
//        for(Enumeration entries = zf.entries(); entries.hasMoreElements();)
//        {
//            ZipEntry ze = (ZipEntry)entries.nextElement();
//            if(ze.getName().endsWith("version.properties"))
//                try
//                {
//                    Properties p = new Properties();
//                    try
//                    {
//                        ZipCrypter.ZipCrypterDataEntry output = cryptInputStream(zf.getInputStream(ze), cryptMode, ze.getExtra(), rsaKey);
//                        p.load(new ByteArrayInputStream(output.getData()));
//                    }
//                    catch(IOException e)
//                    {
//                        throw new BuildException("Could not read version.properties!", e);
//                    }
//                    if(p.containsKey("license.name"))
//                    {
//                        LicenseDescriptor ld = new DefaultLicenseDescriptor(p.getProperty("license.name"));
//                        System.out.println((new StringBuilder()).append("Verifying valid license for: ").append(ld.getName()).toString());
//                        LicensingSettings settings = new LicensingSettings();
//                        LicensingCache cache = (LicensingCache)Naming.lookup((new StringBuilder()).append("rmi://").append(settings.getServerHostName()).append(":").append(settings.getServerPort()).append("/").append(settings.getServerRefName()).toString());
//                        if(cache == null)
//                            throw new BuildException("Could not connect to the Licensing Cache!");
//                        LicensingResponse response = cache.checkLicense(ld);
//                        if(!response.isValid())
//                            System.out.println((new StringBuilder()).append("License for file ").append(zf.getName()).append(" is not valid! (").append(response.getMessage()).append(")").toString());
//                        else
//                            System.out.println((new StringBuilder()).append("License ").append(ld.getName()).append(" for file ").append(zf.getName()).append(" is valid!").toString());
//                        return response.isValid();
//                    }
//                }
//                catch(NotBoundException e)
//                {
//                    throw new BuildException("Could not connect to the Licensing Cache!", e);
//                }
//                catch(RemoteException e)
//                {
//                    throw new BuildException("Could not connect to the Licensing Cache!", e);
//                }
//                catch(MalformedURLException e)
//                {
//                    throw new BuildException("The Licensing Cache URL is invalid!", e);
//                }
//        }
//
//        return false;
//    }

    private File getDestinationDir(File file)
    {
        String fileName = file.getName();
        if(!file.isFile() || !fileName.endsWith(".tpi") && !fileName.endsWith(".zip"))
            return null;
        String createDir = fileName.substring(0, fileName.length() - 4);
        File destDir = new File(outputDir, createDir);
        if(destDir.exists())
        {
            System.out.println((new StringBuilder()).append("The directory ").append(destDir.getAbsolutePath()).append(" already exists. Skipping.").toString());
            return null;
        } else
        {
            return destDir;
        }
    }

    public void setFile(String file)
        throws BuildException
    {
        super.setFile(file);
        if(fileTarget.isDirectory())
            System.out.println((new StringBuilder()).append(outputDir.getAbsolutePath()).append(" is a directory.").toString());
        else
            System.out.println((new StringBuilder()).append(outputDir.getAbsolutePath()).append(" is a file.").toString());
    }

    public void setCryptType(String type)
    {
        cryptMode = 2;
    }

    public void setOutputFile(String file)
        throws BuildException
    {
        outputDir = new File(file);
        if(!outputDir.isDirectory() || !outputDir.canWrite())
            throw new BuildException((new StringBuilder()).append("Directory ").append(outputDir.getAbsolutePath()).append(" does not exist!").toString());
        if(!outputDir.canWrite())
            throw new BuildException((new StringBuilder()).append("Directory ").append(outputDir.getAbsolutePath()).append(" is not writable!").toString());
        else
            return;
    }

    public File getOutputFile()
    {
        return outputDir;
    }

    private File outputDir;
}
