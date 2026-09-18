const { ethers } = require("hardhat");

async function main() {
    console.log("Deploying UniversalMatrixLicensing contract...");

    const Licensing = await ethers.getContractFactory("UniversalMatrixLicensing");
    const licensing = await Licensing.deploy();

    await licensing.waitForDeployment();
    const deployedAddress = await licensing.getAddress();

    console.log(`UniversalMatrixLicensing deployed to: ${deployedAddress}`);
    return deployedAddress;
}

if (require.main === module) {
    main().catch((error) => {
        console.error(error);
        process.exitCode = 1;
    });
}

module.exports = { main };

